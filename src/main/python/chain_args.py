linux_d = './komodod -ac_name=MCL '
windows_d = 'komodod.exe -ac_name=MCL '
linux_cli = './komodo-cli -ac_name=MCL '
windows_cli = 'komodo-cli.exe -ac_name=MCL '
marmarad = '-ac_supply=2000000 -ac_cc=2 -addnode=37.148.210.158 -addnode=37.148.212.36 -addnode=149.202.158.145 -addressindex=1 -spentindex=1 -ac_marmara=1 -ac_staked=75 -ac_reward=3000000000'
getinfo = "getinfo"
validateaddress = 'validateaddress'
getaddressesbyaccount = 'getaddressesbyaccount'
listaddressgroupings = 'listaddressgroupings'
setpubkey = 'setpubkey'
getnewaddress = 'getnewaddress'
stop = 'stop'
marmaraunlock = 'marmaraunlock'
marmaralock = 'marmaralock'
getbalance = 'getbalance'
getgenerate = 'getgenerate'
setgenerate = 'setgenerate'  # + True "number" or False
getaddressbalance = 'getaddressbalance'  # +  '{"addresses": ["address"]}'
convertpassphrase = 'convertpassphrase'  # + "agamapassphrase"
importprivkey = 'importprivkey'  # + "wifkey"
dumpprivkey = 'dumpprivkey'  # + "address"
marmarainfo = 'marmarainfo'  # firstheight + lastheight + minamount + maxamount + pubkey
sendrawtransaction = 'sendrawtransaction'  # + hex
marmarareceivelist = 'marmarareceivelist'  # + pubkey + maxage
sendtoaddress = 'sendtoaddress'  # + amount
marmaracreditloop = 'marmaracreditloop'  # + txid
marmarareceive = 'marmarareceive'  # case 1: + senderpk + amount + currency + matures + '{"avalcount":"n"}' case 2:
# senderpk batontxid '{"avalcount":"n"}'
marmaratransfer = 'marmaratransfer'  # + receiverpk + '{"avalcount":"n"}' + requesttxid
marmaraissue = 'marmaraissue'  # receiverpk + '{"avalcount":"n", "autosettlement":"true"|"false",
# "autoinsurance":"true"|"false", "disputeexpires":"offset", "EscrowOn":"true"|"false", "BlockageAmount":"amount" }'
# + requesttxid
marmaraholderloops = 'marmaraholderloops'  # firstheight + lastheight + minamount + maxamount + pk + [currency]
getaddresstxids = 'getaddresstxids'  # '{"addresses": ["address"], "start": 799712,  "end": 799734}'
marmaralistactivatedaddresses = 'marmaralistactivatedaddresses'
gettransaction = 'gettransaction'  # + txid
