
import os
import logging
import random
import numpy as np
import yaml
import concurrent
import json
import pathlib

from concurrent.futures import ThreadPoolExecutor
try:
    from box import Box
except ModuleNotFoundError:
    Box = None


class ConfigBox(dict):
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError as exc:
            raise AttributeError(key) from exc

    @classmethod
    def from_mapping(cls, value):
        if isinstance(value, dict):
            return cls({k: cls.from_mapping(v) for k, v in value.items()})
        if isinstance(value, list):
            return [cls.from_mapping(v) for v in value]
        return value


def load_yaml_config(config_path):
    if Box is not None:
        return Box.from_yaml(filename=config_path, Loader=yaml.FullLoader)
    with open(config_path, "r", encoding="utf-8") as file:
        return ConfigBox.from_mapping(yaml.load(file, Loader=yaml.FullLoader))

def get_game_config_path(game):
    config_root = './gamingbench/configs/game_configs'
    if game == 'tictactoe':
        return os.path.join(config_root, 'tictactoe.yaml')
    elif game == 'connect4':
        return os.path.join(config_root, 'connect4.yaml')
    elif game == 'backgammon':
        return os.path.join(config_root, 'backgammon.yaml')
    elif game == 'breakthrough':
        return os.path.join(config_root, 'breakthrough.yaml')
    elif game == 'first_sealed_auction':
        return os.path.join(config_root, 'first_sealed_auction.yaml')
    elif game == 'gin_rummy':
        return os.path.join(config_root, 'gin_rummy.yaml')
    elif game == 'liars_dice':
        return os.path.join(config_root, 'liars_dice.yaml')
    elif game == 'negotiation':
        return os.path.join(config_root, 'negotiation.yaml')
    elif game == 'nim':
        return os.path.join(config_root, 'nim.yaml')
    elif game == 'pig':
        return os.path.join(config_root, 'pig.yaml')
    elif game == 'kuhn_poker':
        return os.path.join(config_root, 'kuhn_poker.yaml')
    elif game == 'kuhn_poker_history10':
        return os.path.join(config_root, 'kuhn_poker_history10.yaml')
    else:
        raise NotImplementedError


def load_game(game_config_path):
    from gamingbench import games

    game_config = load_yaml_config(game_config_path)
    return getattr(games, game_config.game_name)()


def load_config(config_path):
    return load_yaml_config(config_path)


def load_agent(agent_config_path, **kwargs):
    from gamingbench import agents

    agent_config = load_yaml_config(agent_config_path)
    agent_class = getattr(agent_config, "agent_class", agent_config.agent_name)
    return getattr(agents, agent_class)(agent_config, **kwargs)


def load_model(model_config_path):
    from gamingbench import models

    model_config = load_yaml_config(model_config_path)
    return getattr(models, model_config.model_type)(model_config)


def set_seed(seed):
    np.random.seed(seed)
    random.seed(seed)


def get_logger(logger_path, debug=False, rm_existed=False):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(ch)

    if rm_existed and os.path.exists(logger_path):
        os.remove(logger_path)

    fh = logging.FileHandler(logger_path)
    fh.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(fh)

    return logger


def parallel_func(worker, arg_list, num_workers=20):
    results = []
    futures = []
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        for idx, arg in enumerate(arg_list):
            futures.append(executor.submit(worker, arg))

        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())
    return results


def load_jsonl(path):
    result = []
    with open(path, 'r') as f:
        for l in f.readlines():
            r = json.loads(l)
            result.append(r)
    return result


def save_jsonl(results, path):
    with open(path, 'w') as f:
        for r in results:
            f.writelines(json.dumps(r) + '\n')


class LLMBenchLogger:
    _active_logger = None
    _loggers = {}

    def __new__(cls, logger_path, debug=False, rm_existed=False):
        if logger_path is None:
            if cls._active_logger is None:
                cls._active_logger = cls._configure_logger(
                    None, debug, rm_existed)
            return cls._active_logger

        logger_key = os.path.abspath(logger_path)
        if rm_existed and logger_key in cls._loggers:
            for handler in cls._loggers[logger_key].handlers[:]:
                handler.close()
                cls._loggers[logger_key].removeHandler(handler)
            del cls._loggers[logger_key]

        if logger_key not in cls._loggers:
            cls._loggers[logger_key] = cls._configure_logger(
                logger_path, debug, rm_existed)

        cls._active_logger = cls._loggers[logger_key]
        return cls._active_logger

    @staticmethod
    def _configure_logger(logger_path, debug, rm_existed):
        if logger_path is None:
            logger_name = __name__
        else:
            game_name = os.path.basename(os.path.dirname(logger_path))
            run_name = os.path.splitext(os.path.basename(logger_path))[0]
            logger_name = f"{__name__}.{game_name}.{run_name}"
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.INFO)
        logger.propagate = False

        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)

        ch = logging.StreamHandler()
        ch.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        logger.addHandler(ch)

        if logger_path is None:
            return logger

        pathlib.Path(os.path.dirname(logger_path)).mkdir(parents=True, exist_ok=True)

        if rm_existed and os.path.exists(logger_path):
            os.remove(logger_path)

        fh = logging.FileHandler(logger_path)
        fh.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        logger.addHandler(fh)

        return logger
