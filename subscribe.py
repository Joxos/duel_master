def subscribe(*event_classes):
    def decorator(fn):
        if not hasattr(fn, "_event_subscriptions"):
            fn._event_subscriptions = []
        fn._event_subscriptions.extend(event_classes)
        return fn
    return decorator