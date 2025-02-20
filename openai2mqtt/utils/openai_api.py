def get_assistants(client):
    return list(client.beta.assistants.list(order="asc", limit="20"))


def get_assistant_by_name(client, name):
    assistants = get_assistants(client)
    return [assistant for assistant in assistants if assistant.name == name][0]
