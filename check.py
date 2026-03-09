import asyncio
import aiohttp
from aiohttp import TCPConnector, ClientTimeout
import random
import string
import winsound

available_file = "available_gamertags.txt"

letters = string.ascii_lowercase
letters_numbers = string.ascii_lowercase + string.digits

BANNER = """
\033[35m╔══════════════════════════════════════════════════════════════════════════╗
║                                                                          ║
║   ██╗  ██╗███████╗██████╗  ██████╗                                       ║
║   ╚██╗██╔╝██╔════╝██╔══██╗██╔═══██╗                                      ║
║    ╚███╔╝ █████╗  ██████╔╝██║   ██║                                      ║
║    ██╔██╗ ██╔══╝  ██╔══██╗██║   ██║                                      ║
║   ██╔╝ ██╗███████╗██║  ██║╚██████╔╝                                      ║
║   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝ ╚═════╝                                       ║
║                                                                          ║
║   ░██████╗░░█████╗░███╗░░░███╗███████╗██████╗░████████╗░█████╗░░██████╗░ ║
║   ██╔════╝░██╔══██╗████╗░████║██╔════╝██╔══██╗╚══██╔══╝██╔══██╗██╔════╝░ ║
║   ██║░░██╗░███████║██╔████╔██║█████╗░░██████╔╝░░░██║░░░███████║██║░░██╗░ ║
║   ██║░░╚██╗██╔══██║██║╚██╔╝██║██╔══╝░░██╔══██╗░░░██║░░░██╔══██║██║░░╚██╗ ║
║   ╚██████╔╝██║░░██║██║░╚═╝░██║███████╗██║░░██║░░░██║░░░██║░░██║╚██████╔╝ ║
║   ░╚═════╝░╚═╝░░╚═╝╚═╝░░░░░╚═╝╚══════╝╚═╝░░╚═╝░░░╚═╝░░░╚═╝░░╚═╝░╚═════╝░ ║
║                                                                          ║
║              ★ ════════════════════════════════════ ★                    ║
║                    【 Xbox Gamertag Checker 】                           ║
║              ★ ════════════════════════════════════ ★                    ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝\033[0m
"""


def generate_username(length, use_numbers):
    first = random.choice(letters)
    chars = letters_numbers if use_numbers else letters
    rest = "".join(random.choice(chars) for _ in range(length - 1))
    return first + rest


async def check_gamertag(session, username):

    url = f"https://xboxgamertag.com/search/{username}"

    for attempt in range(3):
        try:

            async with session.get(url) as response:

                text = await response.text()

                if "Gamertag doesn't exist" in text:

                    print(f"\r{' ' * 50}\r", end="")
                    print(f"✓ 利用可能 → {username}")
                    winsound.Beep(1000, 300) 
                    with open(available_file, "a") as f:
                        f.write(username + "\n")

                else:
                    print(f"\rチェック中 → {username}{' ' * 10}", end="", flush=True)

                return

        except asyncio.TimeoutError:
            if attempt < 2:
                await asyncio.sleep(0.1)
            else:
                print(f"\r× タイムアウト{' ' * 20}", end="", flush=True)
        except:
            if attempt < 2:
                await asyncio.sleep(0.1)
            else:
                print(f"\r× リクエスト失敗{' ' * 20}", end="", flush=True)


async def worker(session, length, use_numbers):

    while True:

        username = generate_username(length, use_numbers)

        await check_gamertag(session, username)


async def main():

    print(BANNER)

    try:
        length_input = input("ゲーマータグの長さ (デフォルト: 3): ").strip()
        length = int(length_input) if length_input else 3

        numbers_input = input("数字を含める？ (y/n, デフォルト: n): ").strip().lower()
        use_numbers = numbers_input == "y"

        threads_input = input("同時チェック数 (デフォルト: 50): ").strip()
        threads = int(threads_input) if threads_input else 50
    except (EOFError, KeyboardInterrupt):
        print("\n終了します...")
        return

    print(f"\n設定: 長さ={length}, 数字={'あり' if use_numbers else 'なし'}, 同時={threads}")
    print("開始します...\n")

    timeout = ClientTimeout(total=10, connect=5)
    connector = TCPConnector(
        limit=threads,
        limit_per_host=threads,
        ttl_dns_cache=300,
        enable_cleanup_closed=True,
        force_close=False,
    )

    async with aiohttp.ClientSession(
        connector=connector,
        timeout=timeout,
        headers={"Connection": "keep-alive"}
    ) as session:

        tasks = []

        for _ in range(threads):
            tasks.append(worker(session, length, use_numbers))

        await asyncio.gather(*tasks)


asyncio.run(main())