import requests
import time
import sys
from collections import deque

# ==================== KONFIG ====================
URL           = "https://luckywatch.pro/api/macros/tasks/"
DASHBOARD_URL = "https://luckywatch.pro/api/macros/dashboard/"
CAPTCHA_HASH  = "df00e07a0ea0decc7439d0e3effdc5c4"

DAILY_LIMIT  = 830
HOURLY_LIMIT = 80
RUN_TARGET   = 85
TIME_BUDGET  = 3300

MAX_CONSECUTIVE_FAILS = 15
FIXED_DELAY           = 20
MAX_EARLY_RETRY       = 4
EARLY_WAIT            = 15
STUCK_COOLDOWN        = 45

USERID = "639147"
TOKEN  = "c604928d58bd82841b120ef0f46861e3"

FP = (
    "R1uiSpIgn9rTaoYymse6dg==:9ESFNRJExMjBoXB8DViNKhgWwJD/Pan3zn3ION+4ffR5KwzVLh4ZWxk6n6/hBOMSLi95fKX7MXKo1mUB7l2B/aeazXHKJss3J+FVWG71towOqqL2PP7seqPyo8e295f/edLBaGzn5Q2kbgdbgdBRW5UxK3B+Sn8/SqkhDf44awjTymxCoIC+pw1bKggeCqM/saRj/OwXsX5EFUC+YMv5d2Yi56o5+intl/Q0Qo4e1bsGOe3/ihZkUAci0dH9SIamTuCZKtl+Bh+GcGaARBSmUfYP8ku+PavTxqWHIeH5oq46o2XgG0/dMbI1VH9n1zVAx1ysQQIF6BCTTjdjCrro9ORUCf1L0gCbO/UU4Nrxi198ReaTfPR+BPaEPyDcIvc+/YlqThPaKrL/GOISKl07iw9/eM4nj/MSGHKpK7xaCf9NX2NOpIOMq2GQybAEIj4lFGXuydGbjnjRIOdIKUOEoUpccHUfKkrJLPAlCVS9zhI841eC7wOxYPRRUshJTKD9VNL3eTCxc2vhYsfx3WbCC2x92272z0ztrd8NbvfGxlzPKSNt2bt5HTpR3dEEl9W+Q7nUP8rlePlyjuW2OEOYORh6Q2fleE8Dd57O6PF+D3e/YwsdWaPHyBzR95d2k+Eaa+bNH064HiWQHtK86VjO9q3Cp372swB+snOHZJc/AWwRhJXpSTgwPMnTqVjq9eRxMVYgZgaSxYtp4eosimtJVQk6KcxQR/1djqnXtSo+WKasshDb/12klZdJtbQq11+n7Y6rB36OGkdByscwCQG+cHhymgNZHXLQVQji3JHExqBGLjUilSBWf6Wi0GOC9XqSEsqw5lUKvppN6Avp8BE+3BbCvjMMCGWMCKHchky9HfwlD7L+40HYYTlNcvEXgvCZr7VtR3n9r9AwZKKWSpMf0HUqkZ2QlkHvUkRkoR0BMbmY7J9ijdxbgjI9U2kYzWhM85ALa1vlTVa4mjnBiMo6bgb/+DktAnI77Hle/+cbVwzjbkP/Di2/ohmLHvucdN0+FuE5klXQUwh822Sjk5ekUjvW9hPr7otabaznzkIra8+PZw7HaX+4fz62v5DPw5/Jg7Ba03y8hJVOZHDMAZF9L1LOZbUjdOlBRNKh5TZngdBrc+8HVRH9cSQ3HdCB4SW9Nqp8j9XuAMWfsfz+lL5KGxe0e7DLoWO//FIunvKEi7I4JT9842zaivw15l3jHnKSiSIdFkfRpmDSO2hsJIWuO6PxXeoN2ZfOwxG45qfDOefLk2gbYuQLV9bb1sX4hRQJ6n0VYd3+BhV7ViFoajBuNpNFHXa/miNzgqwhHHo6yrsNiU3RkAZ/TMflemhZb5ENzmwEdqQ5Zx1TEL69/vPXysAFsUHX2uVgAOiEzHWuHRhOeQekQ729AeMaNHX+vfUNLiRVHchW2C4foFCC5xbyHDyNEInIR6xwnvHlxRpN78yDSnUyLaM36TmBZxdYaH/"
)

GET_META   = "9FG9ZDl9s9LCUNAvaP0OUg==:pc2JUqIQOoycvD4Ad6cWly5oj9JmY0crACAOsMJW3V/dklR+wOE3Lp1lcew/7RIf"
GET_SIG    = "587099d039f5e0adf45e01dd89eb9ad050d97845788938538d80a6a1a56a7c8b"
CHECK_META = "9wXGcm2vN9t3AXdDeHR1SQ==:lIS3JsnwmGS7ptAhKzSHckjvS16sccI8sRiln1O7A9d/XJuy3VMwbZYmXmEfF1O3"
CHECK_SIG  = "88fbb4dd8ffc912f3f72a9098393fef6ec39d019105515a00bc253c775b39f84"

DASHBOARD_META = "Hq6SwbdZHY5cLKquq3KbSw==:yjK2VSrJWKe93yLA4S+GIDVLVUkvositA77QtJDFv6rveVCnTpksF8c+XcdfrgV"
DASHBOARD_SIG  = "9ed0df41c5e0c4eb48b97c253c7cec1f6587f8b4a33f4e0e03e093542c2106ec"


def log(msg):
    print(f"{msg}", flush=True)


TASK_TIMES = deque()


def _trim_window():
    now = time.time()
    while TASK_TIMES and now - TASK_TIMES[0] >= 3600:
        TASK_TIMES.popleft()


def wait_for_hourly_slot():
    while True:
        _trim_window()
        if len(TASK_TIMES) < HOURLY_LIMIT:
            return True
        wait = 3600 - (time.time() - TASK_TIMES[0]) + 2
        if (time.time() - START_TIME + wait) >= TIME_BUDGET:
            log(f"Hourly slot butuh tunggu {wait:.0f}s, tapi udah lewat budget — stop.")
            return False
        log(f"Hourly limit {len(TASK_TIMES)}/{HOURLY_LIMIT} — tunggu {wait:.0f}s ({wait/60:.1f} menit)...")
        time.sleep(wait)


def headers_():
    return {
        "user-agent": "Mozilla/5.0 (Linux; Android 13; 33) Redmi M2101K7BNY Mobile",
        "userid": USERID,
        "token": TOKEN,
        "content-type": "application/x-www-form-urlencoded",
    }


def fetch_dashboard():
    body = {"type": "dashboard", "_v": "1.8",
            "_meta": DASHBOARD_META, "_sig": DASHBOARD_SIG}
    return requests.post(DASHBOARD_URL, headers=headers_(), data=body, timeout=30)


def get_task():
    body = {"method": "getTask", "captcha_hash": CAPTCHA_HASH, "fp": FP,
            "_v": "1.9", "_meta": GET_META, "_sig": GET_SIG}
    return requests.post(URL, headers=headers_(), data=body, timeout=30)


def check_task(task_id):
    body = {"method": "checkTask", "id": task_id, "captcha_hash": CAPTCHA_HASH,
            "_v": "1.8", "_meta": CHECK_META, "_sig": CHECK_SIG}
    return requests.post(URL, headers=headers_(), data=body, timeout=30)


def complaint_task(task_id):
    body = {"method": "complaint", "error": "same_video_opened", "ads": "",
            "cause": "1", "captcha_hash": CAPTCHA_HASH,
            "_v": "1.8", "_meta": CHECK_META, "_sig": CHECK_SIG}
    return requests.post(URL, headers=headers_(), data=body, timeout=30)


START_TIME = time.time()


def over_budget():
    return (time.time() - START_TIME) >= TIME_BUDGET


def main():
    log(f"Bot start | run target {RUN_TARGET} | daily cap {DAILY_LIMIT} | "
        f"budget {TIME_BUDGET}s ({TIME_BUDGET/60:.0f}m) | delay {FIXED_DELAY}s")

    daily = 0
    try:
        rd = fetch_dashboard()
        jd = rd.json()
        if jd.get("status") == "ok":
            d = jd.get("data") or {}
            daily = int(d.get("viewCurDay") or 0)
            log(f"Dashboard: viewCurDay={d.get('viewCurDay')} viewAll={d.get('viewAll')} "
                f"balance={d.get('balance')} clovers={d.get('clovers')}")
            log(f"Mulai dari {daily}/{DAILY_LIMIT}")
        else:
            log(f"Dashboard gagal ({jd}), mulai dari 0")
    except Exception as e:
        log(f"Dashboard error ({e}), mulai dari 0")

    if daily >= DAILY_LIMIT:
        log(f"Server udah {daily} >= {DAILY_LIMIT}, stop. (exit 0)")
        return

    fails = 0
    claimed_this_run = 0

    while daily < DAILY_LIMIT:
        if over_budget():
            log(f"Time budget habis. Claim run ini: {claimed_this_run}. (exit 0)")
            return
        if claimed_this_run >= RUN_TARGET:
            log(f"Run target {RUN_TARGET} tercapai. Total hari ini: {daily}/{DAILY_LIMIT}. (exit 0)")
            return
        if fails >= MAX_CONSECUTIVE_FAILS:
            log(f"{fails} gagal berturut-turut — stop. Cek TOKEN / CAPTCHA_HASH. (exit 1)")
            sys.exit(1)

        try:
            if not wait_for_hourly_slot():
                log(f"Time budget habis (nunggu slot). Claim run ini: {claimed_this_run}. (exit 0)")
                return

            log(f"getTask  [{daily}/{DAILY_LIMIT}] run {claimed_this_run}/{RUN_TARGET}")
            r1 = get_task()

            if r1.status_code != 200:
                log(f"  HTTP {r1.status_code}: {r1.text[:100]}")
                fails += 1; time.sleep(20); continue

            try:
                j1 = r1.json()
            except ValueError:
                log(f"  bukan JSON: {r1.text[:100]}")
                fails += 1; time.sleep(20); continue

            if j1.get("status") != "ok":
                msg = j1.get("message", "")
                log(f"  getTask status != ok: {msg}")
                if "limit_hour" in msg.lower():
                    log(f"Server hourly cap. Claim run ini: {claimed_this_run}. (exit 0)")
                    return
                fails += 1
                time.sleep(10 if "Lock wait" in msg else 30)
                continue

            data = j1.get("data") or {}
            task_id = data.get("id")

            if not task_id:
                log(f"  no task id: {data}")
                fails += 1; time.sleep(20); continue

            log(f"  -> task {task_id}")
            time.sleep(FIXED_DELAY)

            attempt = 0
            while True:
                if over_budget():
                    log(f"Time budget habis di tengah task. Claim run ini: {claimed_this_run}. (exit 0)")
                    return

                tag = f" (retry {attempt}/{MAX_EARLY_RETRY})" if attempt else ""
                log(f"  -> checkTask {task_id}{tag}")
                r2 = check_task(task_id)

                if r2.status_code != 200:
                    log(f"  HTTP {r2.status_code}: {r2.text[:100]}")
                    fails += 1; time.sleep(15); break

                try:
                    j2 = r2.json()
                except ValueError:
                    log(f"  bukan JSON: {r2.text[:100]}")
                    fails += 1; time.sleep(15); break

                if j2.get("status") == "ok":
                    d = j2.get("data") or {}
                    reward  = d.get("reward", "?")
                    balance = d.get("balance", "?")
                    daily += 1
                    claimed_this_run += 1
                    fails = 0
                    TASK_TIMES.append(time.time())
                    log(f"  CLAIMED reward={reward} balance={balance} | "
                        f"total {daily}/{DAILY_LIMIT} | run {claimed_this_run}/{RUN_TARGET} | "
                        f"{(time.time()-START_TIME)/60:.1f}m")
                    break

                msg = (j2.get("message") or "").lower()

                if "limit_hour" in msg:
                    log(f"Server hourly cap. Claim run ini: {claimed_this_run}. (exit 0)")
                    return

                if "too early" in msg:
                    if attempt < MAX_EARLY_RETRY:
                        attempt += 1
                        log(f"  too early, tunggu {EARLY_WAIT}s lalu retry")
                        time.sleep(EARLY_WAIT)
                        continue
                    log(f"  task {task_id} stuck ({MAX_EARLY_RETRY}x too early) → complaint")
                    try:
                        rc = complaint_task(task_id)
                        log(f"  complaint HTTP {rc.status_code}: {rc.text[:80]}")
                    except Exception as e:
                        log(f"  complaint error: {e}")
                    log(f"  cooldown {STUCK_COOLDOWN}s sebelum getTask lagi")
                    time.sleep(STUCK_COOLDOWN)
                    fails += 1
                    break

                log(f"  checkTask status != ok: {j2}")
                if "Lock wait" in msg:
                    fails += 1; time.sleep(10); break
                fails += 1; time.sleep(15)
                break

        except KeyboardInterrupt:
            log(f"Stop manual. Claim run ini: {claimed_this_run}. (exit 0)")
            return
        except requests.exceptions.RequestException as e:
            log(f"Network: {e}")
            fails += 1; time.sleep(20)
        except Exception as e:
            log(f"Error: {e}")
            fails += 1; time.sleep(20)

    log(f"SELESAI — total {daily}/{DAILY_LIMIT}, run ini {claimed_this_run} "
        f"dalam {(time.time()-START_TIME)/60:.1f} menit. (exit 0)")


if __name__ == "__main__":
    main()
