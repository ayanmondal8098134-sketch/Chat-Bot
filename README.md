# My OpenAI Chatbot

A small Python chatbot that can optionally search the web for up-to-date answers. Your API key is used only by the server; it is never sent to the browser.

## Important: protect your key

The key pasted into chat has been exposed. Revoke it in the [OpenAI API keys page](https://platform.openai.com/api-keys) before doing anything else, then create a new key. Never put a key in `public/`, JavaScript, GitHub, or a message.

## Run it in VS Code

1. Open this folder in VS Code.
2. Create a file named `.env` by copying `.env.example`.
3. Put your **new** key after `OPENAI_API_KEY=`. Do not use quotation marks.
4. In the VS Code terminal, run:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   flask --app app run --debug
   ```

5. Open the local address shown in the terminal, usually `http://127.0.0.1:5000`.

## Deploy on Vercel

1. Put this project in a private GitHub repository (the `.gitignore` prevents your `.env` from being uploaded).
2. In Vercel, select **Add New → Project**, import that repository, and deploy.
3. In the Vercel project, go to **Settings → Environment Variables** and add:
   - `OPENAI_API_KEY`: your new key
   - `OPENAI_MODEL`: `gpt-5-mini` (or a model available to your project)
4. Redeploy after saving the variables.

Vercel runs `api/chat.py` privately; the web page calls only `/api/chat`.

## How the pipeline works

Browser → `/api/chat` (Python) → OpenAI Responses API → optional web search → answer + source links → browser

The browser keeps the latest short conversation history. The server also trims messages so requests stay reasonable.

## Notes

- Web search can add API cost, so turn it on only when you need current information.
- Add login and rate limits before sharing the app publicly, otherwise strangers could spend your API credits.
- OpenAI’s [Quickstart](https://developers.openai.com/api/docs/quickstart) and [web search guide](https://developers.openai.com/api/docs/guides/tools-web-search) explain the API features used here.
