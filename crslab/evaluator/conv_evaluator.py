# @Time   : 2020/11/30
# @Author : Xiaolei Wang
# @Email  : wxl1999@foxmail.com

# UPDATE:
# @Time   : 2020/12/18
# @Author : Xiaolei Wang
# @Email  : wxl1999@foxmail.com
import os
from collections import defaultdict

import fasttext
from loguru import logger
from nltk import ngrams

from crslab.evaluator.base_evaluator import BaseEvaluator
from crslab.evaluator.utils import nice_report
from .metrics import *
from .resource import resources
from ..config import EMBEDDING_PATH
from ..download import build


class ConvEvaluator(BaseEvaluator):
    """The evaluator specially for conversational model
    
    Args:
        dist_set: the set to record dist n-gram
        dist_cnt: the count of dist n-gram evaluation
        gen_metrics: the metrics to evaluate conversational model, including bleu, dist, embedding metrics, f1
        optim_metrics: the metrics to optimize in training
    """
    def __init__(self):
        super(ConvEvaluator, self).__init__()
        self.dist_set = defaultdict(set)
        self.dist_cnt = 0
        self.gen_metrics = Metrics()
        self.optim_metrics = Metrics()

    def _load_embedding(self, language):
        resource = resources[language]
        dpath = os.path.join(EMBEDDING_PATH, language)
        build(dpath, resource['file'], resource['version'])

        model_file = os.path.join(dpath, f'cc.{language}.300.bin')
        self.ft = fasttext.load_model(model_file)
        logger.info(f'[Load {model_file} for embedding metric')

    def _get_sent_embedding(self, sent):
        return [self.ft[token] for token in sent.split()]

    def gen_evaluate(self, hyp, refs):
        if hyp:
            self.gen_metrics.add("f1", F1Metric.compute(hyp, refs))

            for k in range(1, 5):
                self.gen_metrics.add(f"bleu@{k}", BleuMetric.compute(hyp, refs, k))
                for token in ngrams(hyp, k):
                    self.dist_set[f"dist@{k}"].add(token)
            self.dist_cnt += 1

            hyp_emb = self._get_sent_embedding(hyp)
            ref_embs = [self._get_sent_embedding(ref) for ref in refs]
            self.gen_metrics.add('greedy', GreedyMatch.compute(hyp_emb, ref_embs))
            self.gen_metrics.add('average', EmbeddingAverage.compute(hyp_emb, ref_embs))
            self.gen_metrics.add('extreme', VectorExtrema.compute(hyp_emb, ref_embs))

    def report(self):
        for k, v in self.dist_set.items():
            self.gen_metrics.add(k, AverageMetric(len(v) / self.dist_cnt))
        reports = [self.gen_metrics.report(), self.optim_metrics.report()]
        logger.info('\n' + nice_report(aggregate_unnamed_reports(reports)))

    def reset_metrics(self):
        self.gen_metrics.clear()
        self.dist_cnt = 0
        self.dist_set.clear()
        self.optim_metrics.clear()
