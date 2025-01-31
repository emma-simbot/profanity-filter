"""RESTful web service for profanity filtering"""

import logging
import pathlib
from contextlib import suppress

import uvicorn
from appdirs import AppDirs
from fastapi import FastAPI, Path, Request, Response, status

from profanity_filter.config import DEFAULT_CONFIG
from profanity_filter.profanity_filter import APP_NAME, ProfanityFilter
from profanity_filter.types_ import Word

logger = logging.getLogger(__name__)

def create_profanity_filter() -> ProfanityFilter:
    app_dirs = AppDirs(APP_NAME)
    config_path = pathlib.Path(app_dirs.user_config_dir) / 'web-config.yaml'
    with suppress(FileExistsError):
        DEFAULT_CONFIG.to_yaml(config_path, exist_ok=False)
    return ProfanityFilter.from_yaml(config_path)


app = FastAPI()
pf = create_profanity_filter()


@app.get('/healthcheck')
async def root(response: Response) -> str:
    """Ping the API to make sure it is responding."""
    response.status_code = status.HTTP_200_OK
    return "success"


@app.post(path='/censor-word/{word}', response_model=Word)
async def censor_word(word: str = Path(..., title='Word to censor', description='Word to censor')):
    return pf.censor_word(word)


@app.post(path='/is-profane')
async def is_profane(request: Request) -> bool:
    """Determine whether or not the provided text contains profanity."""
    try: 
        request_json = await request.json()
    except Exception as err: 
        raise err
    
    logger.debug(request_json)

    return pf.is_profane(request_json['text'])


if __name__ == "__main__": 
    uvicorn.run(app, host='0.0.0.0')
