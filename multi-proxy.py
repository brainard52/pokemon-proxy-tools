#!/usr/bin/env python3

import requests
from PIL import Image, ImageDraw, ImageColor
from operator import mul
from math import floor
import json
from pathlib import Path
import datetime # TTL for cached queries
import shutil
import base64

headers = {
        'X-Api-Key':'3c3892ce-fdcf-4e50-81b0-7dcd13bfa595',
        'user-agent': 'Multi-proxy V0.0.1 - Discord: brainard50#3809'
        }
set_endpoint = "https://api.pokemontcg.io/v2/sets"
card_endpoint = "https://api.pokemontcg.io/v2/cards"

def mkdir(_dir):
    if not _dir.is_dir():
        if _dir.exists():
            print("{_dir} already exists and is not a directory.")
            exit()
        _dir.mkdir()

cache = Path("cache")
mkdir(cache)
setcache = cache / "sets.json"
cardcache = cache / "cards.json"
imagecache = cache / "images/"
mkdir(imagecache)
combocache = cache / "combined/"
mkdir(combocache)
resulthtml = Path("result.html")

ttl = datetime.timedelta(days=7)



def main():
    cache = {}
    if setcache.is_file():
        try:
            with open(setcache, 'r') as setcache_file:
                cache["sets"] = json.loads(setcache_file.read())
        except Exception as e:
            print(f"Unknown error occurred while attempting to load setcache: {e}")
            return -1
    else:
        cache["sets"] = {}

    if cardcache.is_file():
        try:
            with open(cardcache, 'r') as cardcache_file:
                cache["cards"] = json.loads(cardcache_file.read())
        except Exception as e:
            print(f"Unknown error occurred while attempting to load cardcache: {e}")
            return -1
    else:
        cache["cards"] = {}
    # pyforms-gui open dialogue box to paste 4 decklists
        # for now, open 1.txt, 2.txt, 3.txt, and 4.txt and start from there
    # for each deck, create a list and request each card from pokemontcg.io
        # Note: There should be 60 items in each list
    # write the the first part of the html file
    # iterate over each list simultaneously (card 1 for each list, card 2 for each, etc.)
        # check whether the image is downloaded. Download if not
        # Merge the images for the current iteration into an image and base64 encode it
        # write the line for the image to the html file
    # write the last parts of the html file

    temporary_input_folder = Path('tempinput')
    deck1path = temporary_input_folder / '1.txt'
    deck2path = temporary_input_folder / '2.txt'
    deck3path = temporary_input_folder / '3.txt'
    deck4path = temporary_input_folder / '4.txt'
    with open(deck1path, 'r') as deck1_file, open(deck2path, 'r') as deck2_file, open(deck3path, 'r') as deck3_file, open(deck4path, 'r') as deck4_file:
             deck1 = listify(cache, deck1_file.readlines())
             deck2 = listify(cache, deck2_file.readlines())
             deck3 = listify(cache, deck3_file.readlines())
             deck4 = listify(cache, deck4_file.readlines())

    if len(deck1) != 60:
        print("1.txt does not contain 60 cards")
    if len(deck2) != 60:
        print("2.txt does not contain 60 cards")
    if len(deck3) != 60:
        print("3.txt does not contain 60 cards")
    if len(deck4) != 60:
        print("4.txt does not contain 60 cards")

    html1 = """
<head>
    <style>
        body {
            page-break-inside: avoid;
            text-align: center;
        }
        img {
            min-width: 2.45in;
            min-height:2.45in;
            width: 2.45in;
            height: 3.45in;
        }
    </style>
</head>
<body>
"""
    html2 = """
</body>
    """
    with open(resulthtml, 'w') as outputfile:
        outputfile.write(html1)
        for i in range(60):
            deck1image = queryCardImage(deck1[i]) # return Path
            deck2image = queryCardImage(deck2[i])
            deck3image = queryCardImage(deck3[i])
            deck4image = queryCardImage(deck4[i])
            image_data = combine_images(deck1image, deck2image, deck3image, deck4image)
            image_tag = f'\n<img src="data:image/png;base64,{image_data}" />'
            outputfile.write(image_tag)
        outputfile.write(html2)

    try:
        with open(setcache, 'w') as setcache_file:
            setcache_file.write(json.dumps(cache["sets"], indent=2))
    except Exception as e:
        print(type(e))
        print(f"Unknown error occurred while trying to save setcache. {e}")
        return -1

    try:
        with open(cardcache, 'w') as cardcache_file:
            cardcache_file.write(json.dumps(cache["cards"], indent=2))
    except Exception as e:
        print(type(e))
        print(f"Unknown error occurred while trying to save cardcache. {e}")
        return -1

energy_names = {
        "Grass Energy": "{G}",
        "Fire Energy": "{R}",
        "Water Energy": "{W}",
        "Lightning Energy": "{L}",
        "Psychic Energy": "{P}",
        "Fighting Energy": "{F}",
        "Darkness Energy": "{D}",
        "Metal Energy": "{M}",
        "Fairy Energy": "{Y}"
        }

energy_codes = {
        "{G}": {
            "id": "xy1-132",
            "name": "Grass Energy",
            "code": "XY",
            "setnumber": 132
            },
        "{R}": {
            "id": "xy1-133",
            "name": "Fire Energy",
            "code": "XY",
            "setnumber": 133
            },
        "{W}": {
            "id": "xy1-134",
            "name": "Water Energy",
            "code": "XY",
            "setnumber": 134
            },
        "{L}": {
            "id": "xy1-135",
            "name": "Lightning Energy",
            "code": "XY",
            "setnumber": 135
            },
        "{P}": {
            "id": "xy1-136",
            "name": "Psychic Energy",
            "code": "XY",
            "setnumber": 136
            },
        "{F}": {
            "id": "xy1-137",
            "name": "Fighting Energy",
            "code": "XY",
            "setnumber": 137
            },
        "{D}": {
            "id": "xy1-138",
            "name": "Darkness Energy",
            "code": "XY",
            "setnumber": 138
            },
        "{M}": {
            "id": "xy1-139",
            "name": "Metal Energy",
            "code": "XY",
            "setnumber": 139
            },
        "{Y}": {
            "id": "xy1-140",
            "name": "Fairy Energy",
            "code": "XY",
            "setnumber": 140
            }
        }

def listify(cache, decklist):
    listified_deck = []
    for line in decklist:
        line = " ".join(line.split())
        if line.startswith("Pokémon"):
            continue
        if line.startswith("Trainer"):
            continue
        if line.startswith("Energy"):
            continue
        if line.startswith("Total Cards"):
            continue
        if len(line) == 0:
            continue
        if line.split()[-1] == "PH": #reverse holos fuck things up.
            line = " ".join(line.split()[:-1])
        count = int(line.split()[0])
        # Basic Energies might not have a set specified. If that's the case, the amount of "words" in the line will be 4 and the third word will always be "Energy". They might also be too-specified. In either case, I'll be manually setting them to XY energies since that's easy. Additionally, this may become a nest of fuckery because of the variations of the ptcgo codes. We'll see soon enough.
        if len(line.split()) == 4 and line.split()[2] == "Energy":
            name = " ".join(line.split()[1:-1])
            setnumber = energy_codes[energy_names[name]]["setnumber"]
            setcode = energy_codes[energy_names[name]]["code"]
        elif line.split()[3] == "Energy" and line.split()[4] == "Energy":
            name = energy_codes[line.split()[2]]["name"]
            setnumber = energy_codes[line.split()[2]]["setnumber"]
            setcode = energy_codes[line.split()[2]]["code"]
        else:
            name = " ".join(line.split()[1:-2])
            setnumber = int(line.split()[-1])
            setcode = line.split()[-2]
        if len(setcode) > 3:
            setcode = setcode[:3]

        _set = querySetPTCGOCode(cache, setcode)
        card = queryCard(cache, name, setnumber, setcode)
        for _ in range(count):
            listified_deck.append(card)

        #listified_deck.append( {
        #    "name": name,
        #    "setcode": setcode,
        #    "setnumber": setnumber,
        #    "count": count
        #    } )
    return listified_deck

def combine_images(image1, image2, image3, image4):
    comboname = f"{image1.name.split('.')[0]}_{image2.name.split('.')[0]}_{image3.name.split('.')[0]}_{image4.name.split('.')[0]}.png"
    combopath = combocache / comboname
    if not combopath.is_file():
        border_yellow = "rgb(255,225,101)"
        dpi = (300,300)
        card_dimensions = (2.5, 3.5)
        quarter_card_dimensions =(card_dimensions[0] / 2, card_dimensions[1] / 2) #inches
        quarter_size = (floor(dpi[0] * quarter_card_dimensions[0]),
                        floor(dpi[1] * quarter_card_dimensions[1]))
        # Assume the border will always be 15 px at quarter size. Crop a 10 pixel border and add a 25px border This results in total size reduction of 20 for the quarter size and a total increase of 50 for the final size

        quarter_crop_size = (quarter_size[0] - 20, quarter_size[1] - 20)
        crop_xywh = (10, 10, quarter_size[0] - 10, quarter_size[1] - 10)
        size = (quarter_crop_size[0] * 2 + 50, quarter_crop_size[1] * 2 + 50)
        paste_offset = (25, 25)

        im1 = Image.open(image1)
        im2 = Image.open(image2)
        im3 = Image.open(image3)
        im4 = Image.open(image4)

        im1 = im1.resize(quarter_size)
        im2 = im2.resize(quarter_size)
        im3 = im3.resize(quarter_size)
        im4 = im4.resize(quarter_size)
        im1 = im1.crop(crop_xywh)
        im2 = im2.crop(crop_xywh)
        im3 = im3.crop(crop_xywh)
        im4 = im4.crop(crop_xywh)

        new_im = Image.new("RGBA", size)
        draw = ImageDraw.Draw(new_im)
        draw.rounded_rectangle((0,0,size[0], size[1]), fill=border_yellow, radius=35)
        new_im.paste(im1, paste_offset)
        new_im.paste(im2, (quarter_crop_size[0] + paste_offset[0], 0 + paste_offset[1]))
        new_im.paste(im3, (0 + paste_offset[0], quarter_crop_size[1] + paste_offset[1]))
        new_im.paste(im4, (quarter_crop_size[0] + paste_offset[0], quarter_crop_size[1] + paste_offset[1]))
        new_im.save(combopath, "PNG")
    with open(combopath, 'br') as image:
        image_data = base64.b64encode(image.read()).decode('utf-8')
    return image_data

def queryCardImage(card):
    if 'large' in card['images']:
        url = card['images']['large']
    elif 'small' in card['images']:
        url = card['images']['small']
    else:
        print(f"Error when determining available image size for {card['data']['name']}")
        exit()
    image = imagecache / f"{url.split('/')[-2]}-{url.split('/')[-1]}"
    if not image.is_file():
        print(f"Caching {image}")
        result = requests.get(url)
        if result.status_code !=200:
            print(f"Something went wrong when requesting the image for {card['data']['name']}")
            exit()
        with open(image, 'wb') as image_file:
            image_file.write(result.content)
    else:
        print(f"Found {image} in cache")
    return image

# Can abstract the query and cache easily. TODO
def queryCard(cache, name, setnumber, setcode):
    query = f"{name} {setnumber} {setcode}"
    now = datetime.datetime.now()
    if query in cache["cards"]:
        if datetime.datetime.fromtimestamp(cache["cards"][query]['date']) + ttl > now:
            print(f"Found {query} in cache")
            return cache["cards"][query]['data']

    for _set in cache['sets'][setcode]['data']:
        url = f"{card_endpoint}/{_set['id']}-{setnumber}"
        result = requests.get(url)
        if result.status_code == 200:
            break

    if result.status_code != 200:
        raise ValueError(f"Request for {query} went wrong. Code {result.status_code} returned.")

    cache["cards"][query] = json.loads(result.content.decode(result.encoding))
    cache["cards"][query]['date'] = now.timestamp()
    print(f"Cached {query}")
    return cache["cards"][query]['data']

def querySetPTCGOCode(cache, code):
    now = datetime.datetime.now()
    if code in cache["sets"]:
        if datetime.datetime.fromtimestamp(cache["sets"][code]['date']) + ttl > now:
            print(f"Found {code} in cache")
            return cache["sets"][code]['data']

    result = requests.get(f"{set_endpoint}?q=ptcgoCode:{code}", headers=headers)
    if result.status_code != 200:
        raise ValueError(f"Request for {code} went wrong. Code {result.status_code} returned.")

    # This query may return many sets because things like trainer gallery cards
    # are considered to be part of a different set. The set cache is just a
    # cache of queries as opposed to making a database of sets.
    cache["sets"][code] = json.loads(result.content.decode(result.encoding))
    cache["sets"][code]['date'] = now.timestamp()

    print(f"Cached {code}")
    return cache["sets"][code]['data']


if __name__ == "__main__":

    main()

