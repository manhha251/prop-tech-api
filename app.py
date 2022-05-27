from flask import Flask, redirect
from flask_cors import CORS
from flasgger import Swagger

from blueprints.environments_endpoint import environments

app = Flask(__name__)

app.config['DEBUG'] = True
app.config['JSON_AS_ASCII'] = False
app.config['SWAGGER'] = {
    "swagger_version": "2.0",
    "title": "PropTech API",
    "headers": [
        ('Access-Control-Allow-Origin', '*'),
        ('Access-Control-Allow-Methods', "GET, POST, PUT, DELETE, OPTIONS"),
        ('Access-Control-Allow-Credentials', "true"),
    ],
    "specs": [
        {
            "version": "0.0.1",
            "title": "PropTech API",
            "endpoint": 'v1_spec',
            "description": 'This is the version 1 of our API',
            "route": '/v1/spec',
            # rule_filter is optional
            # it is a callable to filter the views to extract
            # "rule_filter": lambda rule: rule.endpoint.startswith(
            #     'should_be_v1_only'
            # ),
            # definition_filter is optional
            # it is a callable to filter the definition models to include
            # "definition_filter": lambda definition: (
            #         'v1_model' in definition.tags)
        }
    ]
}

app.register_blueprint(environments)
swagger = Swagger(app)


@app.route('/', methods=['GET'])
def index():
    """
    Index page for API
    :return:
    """

    return redirect('/apidocs/index.html')


if __name__ == '__main__':
    CORS(app)
    app.run(threaded=True, port=8080, use_reloader=True, )
