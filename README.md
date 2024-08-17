# MultiPay

A Sentinel DVPN Multipay Transactor

This will run in a loop and prompt you for sentinel wallet addresses and amounts that you would like to send in single transaction (batch sending) based on the seed phrase you specify in the scrtxxs file.

# Installation

* requires sentinel-sdk

* requires >= python 3.10

To install the dependency:

```shell
pip install sentinel-sdk
```

Clone the repository

```shell
git clone https://github.com/MathNodes/MultiPay
```

# Configuration

Within the repository directory, edit the **scrtxxs.py** to your specific parameters. 

* WalletName - The name you will give your sending wallet in the krygin

* HotWalletPW - The Password for your wallet in the keyring

* WalletSeed - The seed phrase of the sending wallet if not already in the keyring. leave blank if you already imported this wallet once before

# Run

To run the MultiPay script do the following:

```shell
python3 SentinelMultiPay.py
```

and follow the on screen prompts

# Logs & Keyring

The log file will be in the following folders

OS X:

```shell
/Users/username/.meile-multi-pay/multipay.log
```

Linux:

```shell
/home/username/.meile-multi-pay/multipay.log
```

This is also the folder the encrypted keyring will reside in. 

# Donations

Because we are working on a small grant with no VC funding, any additional contributions to our developer team is more than certainly welcomed. It will help fund future releases. 

## BTC (Bitcoin)

```
bc1qtvc9l3cr9u4qg6uwe6pvv7jufvsnn0xxpdyftl
```

![BTC](./img/BTC.png)

## DVPN (Sentinel)

```
sent12v8ghhg98e2n0chyje3su4uqlsg75sh4lwcyww
```

![dvpn](./img/DVPN.png)

## XMR (Monero)

```
87qHJPU5dZGWaWzuoC3My5SgoQSuxh4sHSv1FXRZrQ9XZHWnfC33EX1NLv5HujpVhbPbbF9RcXXD94byT18HonAQ75b9dyR
```

![xmr](./img/XMR.png)

## ARRR (Pirate Chain)

```
zs1gn457262c52z5xa666k77zafqmke0hd60qvc38dk48w9fx378h4zjs5rrwnl0x8qazj4q3x4svz
```



![ARRR](./img/ARRR.png)
