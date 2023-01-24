import subprocess
import asyncio
import datetime

wow_folder = f'/mnt/g/Program Files (x86)/World of Warcraft/_retail_'
# raider_folder = f'{wow_folder}/Interface/AddOns/Raider_IO**'
raider_db_folder = f'Interface/AddOns/RaiderIO/db/*'
# raider_db_folder = f'Interface/AddOns/RaiderIO**'

async def main():
    # today = datetime.date.today().strftime('%y%m%d')
    now = datetime.datetime.now().strftime('%y%m%d_%H%M')
    # print(now)
    zipfilename = f'_retail_{now}.zip'
    # wow_folder = f'/mnt/g/Program Files (x86)/World of Warcraft/_retail_'
    # print(zipfilename)
    # cmd = f'zip -r -v \'/mnt/g/games/{zipfilename}\'\
    #         \'{wow_folder}/Fonts\'\
    #         \'{wow_folder}/Interface\'\
    #         \'{wow_folder}/WTF\'\
    #         -x \'{raider_folder}\''

    cmd = f'cd \'{wow_folder}\';\
            zip -r -q \'/mnt/g/games/{zipfilename}\'\
            \'Fonts\'\
            \'Interface\'\
            \'WTF\'\
            -x \'{raider_db_folder}\''
    print(cmd)
    result = subprocess.check_output(cmd, shell=True)
    print(f'{result}') if result else ''

asyncio.get_event_loop().run_until_complete(main())
