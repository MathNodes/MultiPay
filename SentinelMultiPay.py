#!/bin/env python3

import scrtxxs
import requests
import sys
from os import path, mkdir
from urllib.parse import urlparse
from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins

from sentinel_sdk.sdk import SDKInstance
from sentinel_sdk.types import TxParams
from keyrings.cryptfile.cryptfile import CryptFileKeyring
from sentinel_protobuf.cosmos.base.v1beta1.coin_pb2 import Coin
import ecdsa
import hashlib
import bech32
from mospy import Transaction
from grpc import RpcError

from datetime import datetime

MNAPI = "https://api.sentinel.mathnodes.com"
NODEAPI = "/sentinel/nodes/%s"
GRPC = scrtxxs.GRPC
SSL = True
VERSION = 20240817.1914
SATOSHI = 1000000

class MultiPay():
    def __init__(self, keyring_passphrase, wallet_name, seed_phrase = None):
        self.wallet_name = wallet_name
        
        if seed_phrase:
            seed_bytes = Bip39SeedGenerator(seed_phrase).Generate()
            bip44_def_ctx = Bip44.FromSeed(seed_bytes, Bip44Coins.COSMOS).DeriveDefaultPath()
            privkey_obj = ecdsa.SigningKey.from_string(bip44_def_ctx.PrivateKey().Raw().ToBytes(), curve=ecdsa.SECP256k1)
            pubkey  = privkey_obj.get_verifying_key()
            s = hashlib.new("sha256", pubkey.to_string("compressed")).digest()
            r = hashlib.new("ripemd160", s).digest()
            five_bit_r = bech32.convertbits(r, 8, 5)
            account_address = bech32.bech32_encode("sent", five_bit_r)
            print(account_address)
            self.keyring = self.__keyring(keyring_passphrase)
            self.keyring.set_password("meile-multi-pay", wallet_name, bip44_def_ctx.PrivateKey().Raw().ToBytes().hex())
        else:
            self.keyring = self.__keyring(keyring_passphrase)
        
        private_key = self.keyring.get_password("meile-multi-pay", self.wallet_name)
        
        grpcaddr, grpcport = urlparse(GRPC).netloc.split(":")
        
        self.sdk = SDKInstance(grpcaddr, int(grpcport), secret=private_key, ssl=SSL)
        
        self.logfile = open(path.join(scrtxxs.KeyringDIR, "multipay.log"), "a+")
        
        now = datetime.now()
        self.logfile.write(f"\n---------------------------{now}---------------------------\n")
        
    def __keyring(self, keyring_passphrase: str):
        if not path.isdir(scrtxxs.KeyringDIR):
            mkdir(scrtxxs.KeyringDIR)
            
        kr = CryptFileKeyring()
        kr.filename = "keyring.cfg"
        kr.file_path = path.join(scrtxxs.KeyringDIR, kr.filename)
        kr.keyring_key = keyring_passphrase
        return kr 
    
    def get_balance(self, address):
        CoinDict = {'dvpn' : 0, 'scrt' : 0, 'dec'  : 0, 'atom' : 0, 'osmo' : 0}
        #CoinDict = {'tsent' : 0, 'scrt' : 0, 'dec'  : 0, 'atom' : 0, 'osmo' : 0}
        endpoint = "/bank/balances/" + address
        try:
            r = requests.get(MNAPI + endpoint)
            coinJSON = r.json()
        except:
            return None
            
        #print(coinJSON)
        try:
            for coin in coinJSON['result']:
                if "udvpn" in coin['denom']:
                    CoinDict['dvpn'] = int(coin['amount']) 
        except Exception as e:
            print(str(e))
            return None
        return CoinDict
    
    def SendDVPNs(self, addr_amts, wallet_balance: int):
        amt = 0
        
        # Sum total amount
        for amount in addr_amts.values():
            amt += int(amount)
        
        if wallet_balance < int(amt):
            self.logfile.write(f"[sp]: Balance is too low, required: {amt}udvpn, found: {wallet_balance}udvpn\n")
            return False
        
        tx_params = TxParams(
            gas=300000,
            gas_multiplier=1.15,
            fee_amount=30000,
            denom="udvpn"
        )

        tx = Transaction(
            account=self.sdk._account,
            fee=Coin(denom=tx_params.denom, amount=f"{tx_params.fee_amount}"),
            gas=tx_params.gas,
            protobuf="sentinel",
            chain_id="sentinelhub-2",
        )
        
        
        for addr,udvpn in addr_amts.items():
            tx.add_msg(
                tx_type='transfer',
                sender=self.sdk._account,
                recipient=addr,
                amount=udvpn,
                denom="udvpn",
            )
        
        self.sdk._client.load_account_data(account=self.sdk._account)
        
        if tx_params.gas == 0:
            self.sdk._client.estimate_gas(
                transaction=tx, update=True, multiplier=tx_params.gas_multiplier
            )

        tx_height = 0
        try:
            tx = self.sdk._client.broadcast_transaction(transaction=tx)
            
        except RpcError as rpc_error:
            details = rpc_error.details()
            print("details", details)
            print("code", rpc_error.code())
            print("debug_error_string", rpc_error.debug_error_string())
            self.logfile.write("[sp]: RPC ERROR. ")
            return False
        
        if tx.get("log", None) is None:
            tx_response = self.sdk.nodes.wait_for_tx(tx["hash"])
            tx_height = tx_response.get("txResponse", {}).get("height", 0) if isinstance(tx_response, dict) else tx_response.tx_response.height
            
            message = f"Succefully sent {amt}udvpn at height: {tx_height} distributed by {addr_amts}" if tx.get("log", None) is None else tx["log"]
            self.logfile.write(f"[sp]: {message}\n")
            return True
        
        
if __name__ == "__main__":
    print(f"Leeloo Dallas Multipay - A DVPN multipay transactor - by freQniK - version: 5th Element {VERSION}\n\n")
    print("You will be presented with a loop to enter Sentinel wallet addresses and amt. When finished, enter 'done'")
    mp = MultiPay(scrtxxs.HotWalletPW, scrtxxs.WalletName, scrtxxs.WalletSeed)
    
    balance = mp.get_balance(mp.sdk._account.address)
    wallet_balance = float(int(balance.get("dvpn", 0)) / SATOSHI)
    
    print(f"Balance: {wallet_balance} dvpn")
    
    SendDict = {}
    
    while True:
        addr = input("Enter wallet address: ")
        if addr.upper() == "DONE":
            break
        amt = input("Enter dvpn amt to send to wallet: ")
        
        SendDict[addr] = str(int(float(amt) * SATOSHI))
        
    print("The following addresses will receive these repsective amounts: ")
    print(SendDict)
    answer = input("Would you iike to continue (Y/n): ")
    if answer.upper() == "Y":
        if mp.SendDVPNs(SendDict, int(wallet_balance * SATOSHI)):
            print("Transaction completed successfully. Please check the log file")
            print(f"{scrtxxs.KeyringDIR}/multipay.log")
        else:
            print("Something went wrong. Please check the log file.")
            print(f"{scrtxxs.KeyringDIR}/multipay.log")
    else:
        sys.exit(0)
            
        