import asyncio
import aiohttp
import time
from concurrent.futures import ThreadPoolExecutor
import math
import customtkinter as ctk
import threading
import tkinter as tk  

MAX_THREADS = 10
MAX_RETRIES = 5

async def fetch(session, url):
    for attempt in range(MAX_RETRIES):
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=60)) as response:
                return response.status
        except asyncio.TimeoutError:
            await asyncio.sleep(1)
        except Exception:
            break
    return None

async def perform_requests_in_thread(url, request_count, output_widget):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, url) for _ in range(request_count)]
        await asyncio.gather(*tasks)

def start_requests_thread(url, request_count, output_widget):
    asyncio.run(perform_requests_in_thread(url, request_count, output_widget))

def run_requests(url, total_requests, output_widget, start_button):
    output_widget.insert(ctk.END, "Request sending started...\n")
    output_widget.see(ctk.END)

    main(url, total_requests, output_widget)

    start_button.configure(state="normal")

def main(url, total_requests, output_widget):
    start_time = time.time()

    requests_per_thread = math.ceil(total_requests / MAX_THREADS)

    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        futures = [
            executor.submit(start_requests_thread, url, requests_per_thread, output_widget)
            for _ in range(MAX_THREADS)
        ]

        for future in futures:
            try:
                future.result()
            except Exception as e:
                output_widget.insert(ctk.END, f"Error in thread: {e}\n")
                output_widget.see(ctk.END)

    end_time = time.time()
    output_widget.insert(ctk.END, f"\nTotal requests: {total_requests}\n")
    output_widget.insert(ctk.END, f"Execution time: {end_time - start_time:.2f} seconds\n")

def change_theme(theme):
    if theme == "dark":
        ctk.set_appearance_mode("dark")
    else:
        ctk.set_appearance_mode("light")

def run_gui():
    app = ctk.CTk()
    app.title("HTTP Request Sender")
    
    app.geometry("800x600")

    # Create a menu bar
    menubar = tk.Menu(app)
    
    # Directly add theme options to the menu bar
    menubar.add_command(label="Light", command=lambda: change_theme("light"))
    menubar.add_command(label="Dark", command=lambda: change_theme("dark"))
    
    app.config(menu=menubar)

    url_label = ctk.CTkLabel(app, text="Enter URL:")
    url_label.pack(pady=(15, 0))

    url_entry = ctk.CTkEntry(app)
    url_entry.pack(pady=(0, 15), fill='x', padx=30)

    count_label = ctk.CTkLabel(app, text="Enter number of requests:")
    count_label.pack(pady=(15, 0))

    count_entry = ctk.CTkEntry(app)
    count_entry.pack(pady=(0, 15), fill='x', padx=30)

    start_button = ctk.CTkButton(app, text="Start Requests", command=lambda: start_requests(start_button))
    start_button.pack(pady=(10, 15))

    output_text = ctk.CTkTextbox(app)
    output_text.pack(pady=(15, 10), fill='both', expand=True)

    def start_requests(start_button):
        url = url_entry.get()
        try:
            total_requests = int(count_entry.get())
            if total_requests <= 0:
                output_text.insert(ctk.END, "The number of requests must be a positive integer.\n")
                return
            
            start_button.configure(state="disabled")

            threading.Thread(target=run_requests, args=(url, total_requests, output_text, start_button), daemon=True).start()
        
        except ValueError:
            output_text.insert(ctk.END, "Please enter a valid number for the number of requests.\n")

    app.mainloop()

if __name__ == "__main__":
    run_gui()
