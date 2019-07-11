from os import walk, makedirs, path
import json
import re
from shutil import rmtree
import sys
from io import BytesIO
from zipfile import ZipFile
from urllib.request import urlopen
args = sys.argv[1:]



dirs = {"mcasset":"mcasset", "model_item":"mcasset/minecraft-assets-master/assets/minecraft/models/item/stone_button.json", 
    "blockstates":"mcasset/minecraft-assets-master/assets/minecraft/blockstates", "blocktags":"mcasset/minecraft-assets-master/data/minecraft/tags/blocks",
    "out_dp":"generated/datapack", "out_rp":"generated/resourcepack"}
md_counter = 1769000 # pick a high number nobody else would use
bpb = 8 # blocks per block

# global variables :)
model_map = {}
md_tr_mult = 16/bpb
tstp = 1/bpb
low_corn = f'dummy matches ..{int(bpb/2)+1}'
md_scale = tstp*2.2857
model_item = dirs['model_item'].rsplit('/', 1)[1][:-5]
md_orig = md_counter

def mkdir(dr):
    if not path.exists(dr):
        makedirs(dr)
    return(dr)
def rmdir(dr):
    if path.exists(dr):
        rmtree(dr)
    return(dr)
def initfl(flnm):
    mkdir(flnm.rsplit('/', 1)[0])
    with open(flnm, 'w') as outfile:
        outfile.write("")
def download_assets(url="https://github.com/InventivetalentDev/minecraft-assets/archive/master.zip"):
    print(f"downloading mcassets from {url}")
    zip_ref = ZipFile(BytesIO(urlopen(url).read()))
    print(f"unzipping mcassets to "+dirs["mcasset"])
    rmdir(dirs["mcasset"])
    zip_ref.extractall(dirs["mcasset"])
    zip_ref.close()
# argument parsing
for n, arg in enumerate(args):
    if arg.startswith('-'):
        nextarg = args[(n+1)%len(args)]
        if arg=='-d' or arg=='--download_assets':
            cmdargs = []
            if nextarg.startswith("http"):
                cmdargs.append(nextarg)
            download_assets(*cmdargs)
        if arg=='-h' or arg=='--help':
            sys.exit("===== Help page =====\n"+
                    "A tool that makes microblocks for Minecraft\n"+
                    "--argument [input] optional OR <input> mandatory\n"+
                    "command-line arguments:\n"+
                    "-d, --download_assets [url]: re-download mcassets\n"+
                    "-h, --help: show this help page")
# download assets if no assets present
if not path.exists(dirs["mcasset"]):
    download_assets()
rmdir(dirs["out_dp"])
rmdir(dirs["out_rp"])
model_out = json.load(open(dirs['model_item'], 'r'))
if "overrides" not in model_out:
    model_out["overrides"] = []

def convert_blockstate(flnm, data, ylev):
    ret = {}
    global dr
    if "variants" not in data:
        print(f'ERR: {flnm} does not contain variants!')
        return
    if len(data)!=1:
        raise ValueError(f'{flnm} has more than one type of model formatting!')
        return
    if "variants" in data:
        for blockstate, model in data["variants"].items():
            # print(x, y)
            if isinstance(model,list): # if multiple models, use first one (not random)
                model = model[0]
            rt = [0,0,0]
            if "x" in model:
                rt[0] = model["x"]%360
            if "z" in model:
                rt[2] = model["z"]%360
            ret[blockstate] = []
            # rots = [0,90,180,270]
            rots = [0,0,0,0]
            if (rt[0]==0 and rt[2]==0) and len(data["variants"])>1: # save model counts, up/down facing and single-rotation can be screwey looking
                rots = [0,90,180,270]
            for yoff in rots: # return list for nesw orientation of model
                rt[1] = yoff
                if "y" in model:
                    rt[1] = (model["y"]+yoff)%360
                if ((rt[1]-yoff)/90)%2==0:
                    rt[1] = (rt[1]+180)%360 # weird axis reversal
                # print(rt)
                ret[blockstate].append(getCustomModelNumber(model, rt, ylev))
        return(ret)
    return(False)

# specify a model and rotation, get model num back. gen model if need be
def getCustomModelNumber(model, rt, ylev):
    global model_map
    global md_counter
    global model_out
    global md_tr_mult
    if "model" not in model:
        raise ValueError(f'there is no model to downscale!')
    parent = model["model"]
    filecont = json.dumps({
          "parent": parent,
          "display": {
            "head": {
              "rotation": rt,
              "translation": [ 2.2857, (((ylev*md_tr_mult)-7)*2.2857)-14.664, 2.2857 ], 
              "scale": [ md_scale, md_scale, md_scale ]
            }
          }
        }, indent=4)
    if parent not in model_map:
        model_map[parent] = {}
    key = str(rt)+str(ylev)
    if key not in model_map[parent]:
        md_counter = md_counter+1
        directory = dirs['out_rp']+'/assets/minecraft/models/item/'+model_item
        mkdir(directory)
        with open(directory+'/'+str(md_counter)+'.json', 'w') as outfile:
            outfile.write(filecont)
        model_out["overrides"].append({"predicate": {"custom_model_data":md_counter}, "model": f"item/{model_item}/"+str(md_counter)})
        model_map[parent][key] = md_counter
    # print(key, model_map[parent][key])
    return(model_map[parent][key])

dr = dirs['out_dp']+'/data/test/functions'
ns = 'test'
mkdir(f'{dr}/coordloop')

# generate models and their summon mcfunction
drnm = mkdir(f'{dr}/isblock')
ylev_count = 0
for rot in range(4):
    initfl(f'{dr}/coordloop/rot{rot}_isblock.mcfunction')
    open(f'{dr}/coordloop/rot{rot}_isblock.mcfunction', 'a').write(f'say rot{rot}'+"\n")
for x in walk(dirs['blockstates']):
    for y in range(bpb):
    # for y in range(1):
        print(f'generating level: {y}')
        # generate models
        with open(f'{dr}/isblock/isblock.mcfunction', 'a') as fnc_isblock:
            for flnm in sorted(x[2]):
                # flnm = x[2][0]
                if flnm.endswith('.json') and not flnm.startswith('item_frame'):
                # if flnm == "piston.json":
                    blk = flnm[:-5]
                    conv = convert_blockstate(flnm, json.load(open(x[0]+'/'+flnm, 'r')), y)
                    if conv and y==0: # only do first item
                        for rot, (a, b, c, d) in enumerate([
                                ('if', 'if', tstp, tstp),
                                ('unless', 'if', 0, tstp),
                                ('unless', 'unless', 0, 0),
                                ('if', 'unless', tstp, 0)]):
                            for state, nesw_mdls in conv.items():
                                # print(f'{blk}[{state}]')
                                open(f'{drnm}/rot{rot}_{blk}.mcfunction', 'a').write(f'execute if block ~ ~ ~ {blk}[{state}] at @s align y '+
                                    f'run summon minecraft:armor_stand ~{c} ~ ~{d} '+'{Rotation:['+str(rot*90)+'f,0f],Invisible:1b,NoBasePlate:1b,Small:1b,ArmorItems:[{},{},{},{id:"minecraft:'+
                                    model_item+'",Count:1b,tag:{CustomModelData:'+str(nesw_mdls[rot])+'}}],Tags:["tinyrender","dooffset"]}'+"\n")
                            with open(f'{dr}/coordloop/rot{rot}_isblock.mcfunction', 'a') as fnc_isblock:
                                fnc_isblock.write(f"execute if block ~ ~ ~ {blk} run function {ns}:isblock/rot{rot}_{blk}\n")
        if y==0:
            ylev_count = md_counter-md_orig
    break

# static mcfunction scripts with some variable definitions
with open(f'{dr}/coordloop/init.mcfunction', 'w') as outfile:
    outfile.write("scoreboard players set y dummy 1\n"
        +f"scoreboard players set ylev dummy {ylev_count*-1}\n"
        +"kill @e[tag=tinyrender]\n"
        +"execute at @s align x align y align z run summon minecraft:area_effect_cloud ~ ~ ~ {Tags:[\"sl1\"]}\n"
        +f"execute align x align y align z run function {ns}:coordloop/y\n")
with open(f'{dr}/coordloop/y.mcfunction', 'w') as outfile:
    outfile.write("scoreboard players add y dummy 1\n"
        +f"scoreboard players add ylev dummy {ylev_count}\n"
        +"scoreboard players set x dummy 1\n"
        +f"function {ns}:coordloop/x\n"
        +f"execute as @e[tag=tinyrender,tag=dooffset] run function {ns}:coordloop/ylevfixer\n"
        +f"execute as @e[tag=sl1] at @s run tp @s ~ ~{tstp} ~\n"
        +f"execute if score y dummy matches ..{bpb} positioned ~ ~1 ~ run function {ns}:coordloop/y\n"
        +f"execute as @e[tag=sl1] at @s run tp @s ~ ~-{tstp} ~\n")
with open(f'{dr}/coordloop/x.mcfunction', 'w') as outfile:
    outfile.write("scoreboard players add x dummy 1\n"
        +"scoreboard players set z dummy 1\n"
        +f"function {ns}:coordloop/z\n"
        +f"execute as @e[tag=sl1] at @s run tp @s ~{tstp} ~ ~\n"
        +f"execute if score x dummy matches ..{bpb} positioned ~1 ~ ~ run function {ns}:coordloop/x\n"
        +f"execute as @e[tag=sl1] at @s run tp @s ~-{tstp} ~ ~\n")
with open(f'{dr}/coordloop/z.mcfunction', 'w') as outfile:
    outfile.write("scoreboard players add z dummy 1\n"
        +f"execute unless block ~ ~ ~ minecraft:air as @e[tag=sl1] run function {ns}:coordloop/isblock\n"
        +"particle crit \n"
        +"execute at @e[tag=sl1] run particle crit\n"
        +f"execute as @e[tag=sl1] at @s run tp @s ~ ~ ~{tstp}\n"
        +f"execute if score z dummy matches ..{bpb} positioned ~ ~ ~1 run function {ns}:coordloop/z\n"
        +f"execute as @e[tag=sl1] at @s run tp @s ~ ~ ~-{tstp}\n")
with open(f'{dr}/coordloop/isblock.mcfunction', 'w') as outfile:
    outfile.write(f"say isblock\n"+
        f"execute if score x {low_corn} if score z {low_corn} run function {ns}:coordloop/rot0_isblock\n"
        f"execute unless score x {low_corn} if score z {low_corn} run function {ns}:coordloop/rot1_isblock\n"
        f"execute unless score x {low_corn} unless score z {low_corn} run function {ns}:coordloop/rot2_isblock\n"
        f"execute if score x {low_corn} unless score z {low_corn} run function {ns}:coordloop/rot3_isblock\n")
with open(f'{dr}/coordloop/ylevfixer.mcfunction', 'w') as outfile:
    outfile.write("execute store result score @s dummy run data get entity @s ArmorItems[{Count:1b}].tag.CustomModelData\n"
        +"scoreboard players operation @s dummy += ylev dummy\n"
        +"execute store result entity @s ArmorItems[{Count:1b}].tag.CustomModelData int 1 run scoreboard players get @s dummy\n"
        +"tag @s remove dooffset\n"
        +"scoreboard players reset @s dummy\n")



# nesw_regex = re.compile(r'\[0, (\d{1,3}), 0\]')
# mkdir(f'{dr}/isblock')
# for model, rotations in model_map.items():
#     cnt=0
#     for rot in rotations:
#         if nesw_regex.match(rot):
#             # print(f'{rot} matches!')
#             cnt = cnt+1
#     print(f'{cnt} matches for {model}')
with open(dirs['out_rp']+f'/assets/minecraft/models/item/{model_item}.json', 'w') as outfile:
    json.dump(model_out, outfile, indent=4)

print(f'{bpb}³({bpb**3}) tinyblocks: {md_counter-md_orig} models created.')
# print(model_map)