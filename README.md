<b>MicroBlocks for Minecraft, a DataPack</b> <a href="https://discordapp.com/invite/8GxFKYy"><img src="https://img.shields.io/discord/598972098639167497.svg?color=blue&label=discord&logo=discord" alt="Join the chat"></a>

![](https://cdn.discordapp.com/attachments/581495559995654146/598389590818160650/tiny.png)

(A minecraft datapack that aims to create microblocks)

### How to generate
1. download [python3](https://www.python.org/downloads/) via a package manager or manual install.
2. download [main.py](https://github.com/ITZVGcGPmO/microblocks-datapack/blob/master/main.py) to a directory of your choosing.
3. execute main.py under python. (`python3 ./main.py` or `C:\Python36\python.exe main.py` in a terminal cd'ed to your chosen directory)

the script will fetch mcassets from [InventivetalentDev/minecraft-assets](https://github.com/InventivetalentDev/minecraft-assets), then generates+places resource and data packs data in a `generated` directory. (it currently doesn't create pack.mcmeta files, at the moment.)



### In-Game use
0. kill any previous scanpoint/renderpoint entities
1. `execute align x align y align z run summon armor_stand ~.5 ~ ~.5 {Small:1b,Tags:["scanpoint"]}` at scan point
2. `execute align x align y align z run summon armor_stand ~.5 ~ ~.5 {Small:1b,Tags:["renderpoint"]}` at render point
3. `execute as @e[tag=renderpoint,limit=1] at @e[tag=scanpoint,limit=1] run function test:coordloop/init` to "render" microblocks

If tinyblock renderings drop your fps, do `kill @e[tag=tinyrender]`
