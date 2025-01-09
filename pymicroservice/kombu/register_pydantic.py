from functools import partial

from kombu.utils.json import register_type
from pydantic import BaseModel


def class_full_name(clz: type[BaseModel]) -> str:
    return ".".join([clz.__module__, clz.__qualname__])


def _encoder(obj: BaseModel, *args, **kwargs) -> dict:
    return obj.model_dump(*args, **kwargs)


def _decoder(clz: type[BaseModel], data: dict) -> BaseModel:
    return clz(**data)


def register_pydantic_types(models: list[dict[BaseModel]]):
    for model in models:
        register_type(
            model,
            class_full_name(model),
            encoder=_encoder,
            decoder=partial(_decoder, model),
        )
