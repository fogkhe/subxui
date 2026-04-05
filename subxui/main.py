from fastapi import FastAPI, HTTPException, Request, Response

from subxui.models import Target
from subxui.services import Aggregator
from subxui.settings import settings


app = FastAPI(
    openapi_url=None,
)


@app.get(f"/{settings.secret_path}/{{user_id}}")
async def get_subscription(
    request: Request,
    user_id: str,
    target: Target | None = None,
) -> Response:
    if target is None:
        accept = request.headers.get("Accept", "")
        user_agent = request.headers.get("User-Agent", "")

        if "text/html" in accept.lower():
            target = Target.RAW
        elif "clash" in user_agent.lower():
            target = Target.CLASH
        else:
            target = Target.BASE64

    subscription = await Aggregator(settings.subscription_sources).aggregate(
        user_id=user_id,
        target=target,
    )

    if subscription is None:
        raise HTTPException(
            status_code=404,
        )

    return Response(
        content=subscription.content,
        media_type=subscription.media_type,
    )
