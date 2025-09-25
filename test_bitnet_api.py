# test_bitnet_api.py
import os
import sys
import json
import argparse
import requests


def pretty(obj):
    print(json.dumps(obj, ensure_ascii=False, indent=2))

def get_base_url(args):
    return args.base.rstrip("/")

def check_health(base_url, client_id, client_secret):
    try:
        headers = {
            "CF-Access-Client-Id": client_id,
            "CF-Access-Client-Secret": client_secret
        }
        r = requests.get(f"{base_url}/health", timeout=10, headers=headers)
        r.raise_for_status()
        print("✅ /health OK")
        pretty(r.json())
    except Exception as e:
        print("❌ /health failed:", e)
        sys.exit(1)

def call_chat(base_url, model, prompt, max_tokens, temperature, top_p, stops, client_id, client_secret):
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": temperature,
        "top_p": top_p,
        "stop": stops or None,
        # "stream": True  # streaming not implemented in the minimal shim
    }
    headers = {
        "CF-Access-Client-Id": client_id,
        "CF-Access-Client-Secret": client_secret
    }
    r = requests.post(f"{base_url}/v1/chat/completions", json=payload, timeout=120, headers=headers)
    r.raise_for_status()
    return r.json()

def call_completions(base_url, model, prompt, max_tokens, temperature, top_p, stops, client_id, client_secret):
    payload = {
        "model": model,
        "prompt": prompt,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "top_p": top_p,
        "stop": stops or None,
    }
    headers = {
        "CF-Access-Client-Id": client_id,
        "CF-Access-Client-Secret": client_secret
    }
    r = requests.post(f"{base_url}/v1/completions", json=payload, timeout=120, headers=headers)
    r.raise_for_status()
    return r.json()

def main():
    parser = argparse.ArgumentParser(description="Test BitNet FastAPI OpenAI-compatible shim")
    parser.add_argument("--base", default="http://127.0.0.1:19000",
                        help="Base URL (default: http://127.0.0.1:19000)")
    parser.add_argument("--route", choices=["chat", "completions"], default="chat",
                        help="Endpoint to call")
    parser.add_argument("--model", default=os.getenv("BITNET_MODEL", "bitnet-b1.58"),
                        help="Model name string to report")
    parser.add_argument("--cf-client-id", required=True, help="CF Access Client ID header value")
    parser.add_argument("--cf-client-secret", required=True, help="CF Access Client Secret header value")
    parser.add_argument("--prompt", default="Say hello in one short sentence.",
                        help="Prompt text")
    parser.add_argument("--max_tokens", type=int, default=8096)
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--top_p", type=float, default=0.95)
    parser.add_argument("--stop", action="append", default=[],
                        help="Add a stop string. You can pass multiple times.")
    args = parser.parse_args()

    base_url = get_base_url(args)
    print(f"→ Using base URL: {base_url}")
    check_health(base_url, args.cf_client_id, args.cf_client_secret)

    try:
        if args.route == "chat":
            resp = call_chat(base_url, args.model, args.prompt, args.max_tokens, args.temperature, args.top_p, args.stop, args.cf_client_id, args.cf_client_secret)
        else:
            resp = call_completions(base_url, args.model, args.prompt, args.max_tokens, args.temperature, args.top_p, args.stop, args.cf_client_id, args.cf_client_secret)
        print("\n✅ Response:")
        pretty(resp)
        # Optional: print just the text
        if args.route == "chat":
            text = resp["choices"][0]["message"]["content"]
        else:
            text = resp["choices"][0]["text"]
        print("\n📝 Text:\n" + text.strip())
    except requests.HTTPError as he:
        print("❌ HTTP error:", he)
        try:
            pretty(he.response.json())
        except Exception:
            print(he.response.text)
        sys.exit(1)
    except Exception as e:
        print("❌ Error:", e)
        sys.exit(1)

if __name__ == "__main__":
    main()
