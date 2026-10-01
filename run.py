cd ~/meta-bot
cat > run.py << 'PYEOF'
import sys, os, asyncio, inspect
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 50)
print("🚀 Loading bot.so...")
print("=" * 50)

try:
    import bot
    print("✅ bot.so loaded successfully!")
    print()
    print("📦 Available in bot:")
    items = [x for x in dir(bot) if not x.startswith("_")]
    for item in items:
        obj = getattr(bot, item)
        print(f"   • {item} ({type(obj).__name__})")
    print("=" * 50)

    if hasattr(bot, "main") and callable(bot.main):
        print("🚀 Running bot.main()...")
        print("=" * 50)
        result = bot.main()
        if inspect.iscoroutine(result):
            asyncio.run(result)

    elif hasattr(bot, "app"):
        app = bot.app
        if hasattr(app, "run_polling"):
            print("🚀 Starting bot (run_polling)...")
            print("=" * 50)
            app.run_polling()
        elif hasattr(app, "run"):
            print("🚀 Starting Flask app on port 5000...")
            print("=" * 50)
            app.run(host="0.0.0.0", port=5000, debug=False)

    elif hasattr(bot, "start") and callable(bot.start):
        print("🚀 Running bot.start()...")
        result = bot.start()
        if inspect.iscoroutine(result):
            asyncio.run(result)

    elif hasattr(bot, "run") and callable(bot.run):
        print("🚀 Running bot.run()...")
        result = bot.run()
        if inspect.iscoroutine(result):
            asyncio.run(result)

    else:
        print("⚠️  No entry point found. bot.so শুধু load হয়েছে।")

except Exception as e:
    print("❌ Error:")
    import traceback
    traceback.print_exc()
PYEOF

echo "✅ run.py তৈরি হয়েছে"
ls -lh