import json
import os
from aiohttp import web
import tensorflow as tf
from config.paths import Paths

from contexts.prediction.domain.model.prediction import create_prediction
from infrastructure.event_sourced_repos.prediction_repository import PredictionRepository
from library.infrastructure_architecture.event_sourced_architecture.unit_of_work import UnitOfWork


def unit_of_work(request):
    app = request.app
    return UnitOfWork(app['eq'], app['es'])

def _render_json_prediction(prediction):
    body = {
        "sentence": prediction['sentence'],
        "language": prediction['language']
    }
    return body

async def get_api_index(request):
    body = {'status_code': 200}
    return web.json_response(body)

async def predict(request):
    try:
        body = []
        predictions = []
        payload = await request.json()

        for sentence in payload['data']:
            output = request.app['model'].predict([sentence])
            key = output.argmax(axis=1)[0]

            language_mapper_path = os.path.join(Paths.directories['models_dir'], request.app['config']['keras_model_name'], 'language mapper.txt')
            language = exec(open(language_mapper_path).read())
            language = 'en-US' #or langs[key] #TOFIX: Find a better way to load this

            predictions.append({"sentence": sentence,
                                "language": language})

            with unit_of_work(request) as u:
                prediction_repo = u.using(PredictionRepository)

                p = create_prediction(sentence, language)
                prediction_repo.put(p)
                prediction_repo.save_changes()
                
    except ValueError as value_error:
        raise web.HTTPBadRequest(text=str(value_error))

    [body.append(_render_json_prediction(p)) for p in predictions]
    return web.json_response(body)
