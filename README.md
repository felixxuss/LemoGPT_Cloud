# LemoGPT

You have to add an .env file with your OpenAI API Key like this:

```python
OPENAI_API_KEY=<key>
```

### Run localy
When running LemoGPT localy all answers are stored in the ```answers``` folder with a timestamp.

### Run as Docker container
Use following commands to build and use the docker container

```
docker build -t lemo_gpt
docker run --rm -p 8501:8501 lemo_gpt
```
Then go to your browser and visit ```http://localhost:8501/```
