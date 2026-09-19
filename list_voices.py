import asyncio
import edge_tts

async def main():
    voices = await edge_tts.list_voices()
    es_voices = [v for v in voices if v["Locale"].startswith("es-")]
    print(f"Total voces en español: {len(es_voices)}")
    for v in es_voices[:10]:
        print(f"  {v['ShortName']} | {v['Gender']} | {v['Locale']}")

if __name__ == "__main__":
    asyncio.run(main())
