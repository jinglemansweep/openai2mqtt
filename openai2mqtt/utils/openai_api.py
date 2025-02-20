def get_assistants(openai_client):
    return list(openai_client.beta.assistants.list(order="asc", limit="20"))


def get_assistant(openai_client, assistant_id):
    return openai_client.beta.assistants.retrieve(assistant_id=assistant_id)


def get_threads(openai_client):
    return list(openai_client.beta.threads.list(order="asc", limit="20"))


def get_thread(openai_client, thread_id):
    return openai_client.beta.threads.retrieve(thread_id=thread_id)


def get_assistant_by_name(openai_client, name):
    assistants = get_assistants(openai_client)
    return [assistant for assistant in assistants if assistant.name == name][0]
