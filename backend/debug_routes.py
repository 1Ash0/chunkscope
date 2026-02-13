
from app.main import app
from fastapi.routing import APIRoute

def list_routes():
    routes = []
    for route in app.routes:
        if isinstance(route, APIRoute):
            routes.append({
                "path": route.path,
                "name": route.name,
                "methods": route.methods
            })
    
    for r in sorted(routes, key=lambda x: x['path']):
        print(f"{r['methods']} {r['path']} -> {r['name']}")

if __name__ == "__main__":
    list_routes()
