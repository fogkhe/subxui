from fastapi import FastAPI, HTTPException, Request, Response

from subxui.models import Target
from subxui.services import Aggregator
from subxui.settings import settings

app = FastAPI(
    openapi_url=None,
)


@app.get("/{profile_path}/{user_id}")
async def get_user_subscription(
    request: Request,
    profile_path: str,
    user_id: str,
    target: Target | None = None,
) -> Response:
    try:
        profile = next(
            profile for profile in settings.profiles if profile.path == profile_path
        )
    except StopIteration:
        raise HTTPException(
            status_code=404,
        )

    if (profile.per_user and not user_id) or (not profile.per_user and user_id):
        raise HTTPException(
            status_code=404,
        )

    if target is None:
        accept = request.headers.get("Accept", "")
        user_agent = request.headers.get("User-Agent", "")

        if "text/html" in accept.lower():
            target = Target.RAW
        elif "clash" in user_agent.lower():
            target = Target.CLASH
        else:
            target = Target.BASE64

    subscription = await Aggregator(
        profile=profile,
    ).aggregate(
        user_id=user_id,
        target=target,
    )

    if subscription is None:
        raise HTTPException(
            status_code=404,
        )

    headers = {}
    if subscription.user_info:
        headers["subscription-userinfo"] = str(subscription.user_info)

    return Response(
        content=subscription.content,
        media_type=subscription.media_type,
        headers=headers,
    )


@app.get("/{profile_path}")
async def get_subscription(
    request: Request,
    profile_path: str,
    target: Target | None = None,
) -> Response:
    return await get_user_subscription(
        request=request,
        profile_path=profile_path,
        user_id="",
        target=target,
    )
