import requests
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import json

availableUsers = set()
available_batch = []

webhook_url = "YOUR WEBHOOK HERE"

def enviar_batch():
    if available_batch:
        embed = {
            "embeds": [
                {
                    "title": "Usernames Found",
                    "description": "\n".join([f"Username: **{user}** is available ✅" for user in available_batch]),
                    "color": 3066993,
                    "footer": {
                        "text": "https://t.me/MrSh4dow"
                    }
                }
            ]
        }
        try:
            response = requests.post(webhook_url, data=json.dumps(embed), headers={"Content-Type": "application/json"})
            if response.status_code == 204:
                print(f"\n[✅] Batch de {len(available_batch)} usernames enviado correctamente.")
            else:
                print(f"[❌] Error al enviar el batch: {response.status_code}")
            available_batch.clear()  
            time.sleep(1)  
        except Exception as e:
            print(f"[❌] Error al intentar enviar el batch: {e}")

def checkUsername(username: str, total: int, count: int):
    url = f"https://api.phantom.app/user/v1/profiles/{username}"
    start_time = time.time()

    try:
        r = requests.get(url)
        if r.status_code == 404 and r.json()['message'].lower() == "not found":
            availableUsers.add(username)
            available_batch.append(username)  
            
            
            if len(available_batch) >= 15:
                enviar_batch()

            elapsed_time = time.time() - start_time
            current_thread = threading.current_thread().name.split('_')[-1]

            print(f"\r[✅] Username Available: {username} ({count}/{total}) | Current Thread: {current_thread} | Time Taken: {elapsed_time:.2f} seconds", end="", flush=True)
            time.sleep(0.1)

    except Exception as e:
        print(f"[❓] {username} ({e})")

    return availableUsers

def main():
    with open('usernames.txt', 'r') as f:
        usernames = f.read().splitlines()

    total_usernames = len(usernames)

    try:
        threads = int(input("[🟠] Threads: "))
    except Exception:
        threads = 75

    print(f"[✅] Loaded {total_usernames:,} usernames...")
    time.sleep(1.5)

    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {executor.submit(checkUsername, username, total_usernames, idx + 1): username for idx, username in enumerate(usernames)}

        for future in as_completed(futures):
            username = futures[future]
            try:
                future.result()
            except Exception as e:
                print(f"[Error] {username} generated an exception: {e}")

    
    enviar_batch()

    with open('available.txt', 'w') as f:
        for username in availableUsers:
            f.write(f"{username}\n")
        print(f"\n[✅] Wrote to available.txt")

if __name__ == "__main__":
    main()
