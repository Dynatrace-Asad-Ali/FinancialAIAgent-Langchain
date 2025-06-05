from langchain_core.messages import convert_to_messages


def get_pretty_message(message, indent=False) -> str:
    pretty_message = message.pretty_repr(html=True) + "\n"

    if not indent:
        # print(pretty_message)
        return pretty_message

    indented = "\n".join("\t" + c for c in pretty_message.split("\n"))
    # print(indented)
    return indented


def get_pretty_messages(update, last_message=False) -> str:
    is_subgraph = False
    pretty_message:str = ""
    if isinstance(update, tuple):
        ns, update = update
        # skip parent graph updates in the printouts
        if len(ns) == 0:
            return pretty_message

        graph_id = ns[-1].split(":")[0]
        pretty_message = pretty_message + f"Update from subgraph {graph_id}:" + "\n"
        is_subgraph = True

    for node_name, node_update in update.items():
        update_label = f"Update from node {node_name}:"
        if is_subgraph:
            update_label = "\t" + update_label

        pretty_message = pretty_message + update_label + "\n"

        messages = convert_to_messages(node_update["messages"])

        if last_message:
            messages = messages[-1:]

        for m in messages:
            pretty_message = pretty_message + "\n" + get_pretty_message(m, indent=is_subgraph) + "\n"
        return pretty_message
