import json
import os
from aiohttp import web
import tensorflow as tf
from config.paths import Paths
from utilities.log import Log

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

async def get_api_status(request: web.Request) -> web.Response:
    """
    ---
    summary: Get API status
    responses:
      '200':
        description: Api status object
        content:
          application/json:
            schema:
              oneOf:
                - $ref: "#/components/schemas/ApiStatusResponse"
    """
    Log.info("[get get_api_status] New request")
    body = {'status': 'running'}
    return web.json_response(body)

async def predict(request: web.Request) -> web.Response:
    """
    ---
    summary: Get prediction for sentence
    tags:
      - predict
    security:
      - ApiKeyAuth: []
    requestBody:
      required: true
      content:
        application/json:
          schema:
            oneOf:
              - $ref: "#/components/schemas/PredictionRequest"
    responses:
      '200':
        description: Returns predicted language for phrase
        content:
          application/json:
            schema:
              oneOf:
                - $ref: "#/components/schemas/PredictionResponse"
    """
    Log.info("[post predict] New request")
    try:
        body = []
        predictions = []
        payload = await request.json()

        if not 'data' in payload.keys():
            raise web.HTTPBadRequest(text="Missing parameter: data")

        #TODO: Move this block to a model service or into model, need more thought,
        #TODO: as it could also save output and store model information
        for sentence in payload['data']:
            if not 'model' in request.app:
                raise web.HTTPInternalServerError(reason="Missing resource: keras model")
            output = request.app['model'].predict([sentence])
            key = output.argmax(axis=1)[0]

            language_mapper_path = os.path.join(Paths.directories['models_dir'], request.app['config']['keras_model_name'], 'language mapper.txt')
            exec(open(language_mapper_path).read(), globals())
            language = langs[key]

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

