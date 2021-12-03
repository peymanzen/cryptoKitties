import json
import logging
import traceback
import sys
import datetime
from pymongo import MongoClient
from web3 import Web3
from web3._utils.events import get_event_data
from matplotlib import pyplot as plt
import matplotlib.image as img
from matplotlib.gridspec import GridSpec


# MongoClient
logger = logging.getLogger("test")

MONGO_URI = ""  # mongo url
try:
    logger.info("Attempting to connect...")
    client = MongoClient(MONGO_URI)
    db = client.get_database('CryptoKittens')
    records = db.Kittens
    data = db.info
except Exception as e:
    logging.error("Exception seen: " + str(e))
    traceback.print_exc(file=sys.stdout)
# ----------------------------------------------------------------------------------------------------
# json Files
# Contract ABI - This Json file is includes all of functions and events
p = open('cryptoKitten.json')
self = json.load(p)
# ----------------------------------------------------------------------------
# WEB 3 Configuration
CK_token = "0x06012c8cf97bead5deae237070f9587f8e7a266d"  # Crypto Kittens Token
# Eth network Address based on mainnet
url = "https://mainnet.infura.io/v3/ae87372ea6c34da6abe04d65090fb430"
w3 = Web3(Web3.HTTPProvider(url))  # Smart Contract Access by web3
ck_contract = w3.eth.contract(
    address=w3.toChecksumAddress(CK_token), abi=self)


# -------------------Inserting crypto kittens Event and Total Data------------------------------
def ins_info_doc(info):
    try:
        data.insert_one(info)
        return True
    except Exception as e:
        print("An exception occured is ::", e)
        return False

# ---------------------------------------------------------------------------


def info_main(ckc):
    try:
        name = ckc.functions.name().call()
        symbol = ckc.functions.symbol().call()
        totalSupply = ckc.functions.totalSupply().call()
        promo = ckc.functions.promoCreatedCount().call()
        pregnant = ckc.functions.pregnantKitties().call()
        new_Data = {
            'name': name,
            'symbol': symbol,
            'totalSupply': totalSupply,
            'promo': promo,
            'pregnant': pregnant,
            'date': datetime.datetime.now()
        }
        print(ins_info_doc(new_Data))
    except Exception as e:
        print("An exception occured is ::", e)
        return False


info_main(ck_contract)
# -----------------------------------------------------------------------------------
abi_event = {
    'anonymous': False,
    'inputs': [
        {'indexed': False, 'name': 'from', 'type': 'address'},
        {'indexed': False, 'name': 'to', 'type': 'address'},
        {'indexed': False, 'name': 'tokenId', 'type': 'uint256'}],
    'name': 'Transfer',
    'type': 'event'
}
event_sign = w3.sha3(text="Transfer(address,address,uint256)").hex()
logs = w3.eth.getLogs({
    "fromBlock": w3.eth.blockNumber - 100,
    "address": w3.toChecksumAddress(CK_token),
    "topics": [event_sign]
})
recent_tx = [get_event_data(w3.codec, abi_event, log)[
    "args"] for log in logs]
# -----------------------Inserting kitty Data Individually-----------------------


def ins_doc(kitty):
    try:
        records.insert_one(kitty)
        return True
    except Exception as e:
        print("An exception occured is ::", e)
        return False
# ---------------------------------------------------------------------------


def main():
    for i in range(len(recent_tx)):
        try:
            kitty_id = recent_tx[i]['tokenId']
            is_pregnant = ck_contract.functions.isPregnant(kitty_id).call()
            getKitty = ck_contract.functions.getKitty(kitty_id).call()
            ownerOf = ck_contract.functions.ownerOf(kitty_id).call()
            balanceOf = ck_contract.functions.balanceOf(ownerOf).call()
            new_Kittens = {
                'kitty_id': kitty_id,
                'isGestating': getKitty[0],
                'isReady': getKitty[1],
                'cooldownIndex': getKitty[2],
                'nextActionAt': getKitty[3],
                'siringWithId': getKitty[4],
                'birthTime': getKitty[5],
                'matronId': getKitty[6],
                'sireId': getKitty[7],
                'generation': getKitty[8],
                'isPregnant': is_pregnant,
                'ownerOf': ownerOf,
                'balanceOf': balanceOf
            }
            print(ins_doc(new_Kittens))
        except Exception as e:
            print("An exception occured is ::", e)
            return False


main()

fig1, axs1 = plt.subplots(3, 2, figsize=(32, 32), facecolor='white', dpi=60)
# ----------------------------------------------------------------------------

image = img.imread('kitty.jpg')
axs1[0, 0].imshow(image)

# -----------------------Promo and Pregnancy Real time-------------------------------------
lastone1 = data.find().sort([('_id', -1)]).limit(1)
labels = 'promo', 'pregnant'
axs1[1, 1].pie([lastone1[0]['promo'], lastone1[0]['pregnant']],
               labels=labels, shadow=True, startangle=90)

# ------------------------Total Supply------------------------------
l = list(data.find())
data = [x['totalSupply']for x in l]
date = [x['date']for x in l]
axs1[1, 0].plot(date, data)
axs1[1, 0].xaxis.set_tick_params(rotation=10)
axs1[1, 0].set_ylabel('Number')
axs1[1, 0].set_title('Total Supply ')
# -------------------------Pregnant---------------------------------
# m = list(data.find())
kityId = [x['pregnant'] for x in l]
balance = [x['date'] for x in l]
axs1[2, 0].plot(balance, kityId)
axs1[2, 0].set_ylabel('Number')
axs1[2, 0].set_title('pregnant ')
axs1[2, 0].xaxis.set_tick_params(rotation=30)
# -------------------------Balance------------------------------------
m = list(records.find())
kittyId = [x['kitty_id'] for x in m]
balance = [x['balanceOf'] for x in m]
id = map(str, kittyId)
kittiesId = list(id)
width = 0.01       # the width of the bars: can also be len(x) sequence
axs1[0, 1].bar(kittiesId, balance,  label='Balance')
axs1[0, 1].set_ylabel('Balance')
axs1[0, 1].set_title('Kitty ')
axs1[0, 1].legend()
axs1[0, 1].xaxis.set_tick_params(rotation=30)
plt.show()
# ----------------------------------------------------------------------------

