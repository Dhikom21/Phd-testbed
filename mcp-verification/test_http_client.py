import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

async def main():
    async with streamablehttp_client("http://localhost:8080/mcp") as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            print("Tools:", [t.name for t in tools.tools])

            print("\nHealth:")
            r = await session.call_tool("health_check", {})
            print(" ", r.content[0].text)

            print("\nSafe action (should be ALLOWED):")
            r = await session.call_tool("kubectl_action", {
                "verb": "get", "resource": "deployments", "namespace": "agent-sandbox"
            })
            print(" ", r.content[0].text[:200])

            print("\nProtected delete (should be BLOCKED):")
            r = await session.call_tool("kubectl_action", {
                "verb": "delete", "resource": "deployments/payments", "namespace": "agent-sandbox"
            })
            print(" ", r.content[0].text[:200])

asyncio.run(main())
