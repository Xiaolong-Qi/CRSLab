# @Time   : 2020/11/30
# @Author : Xiaolei Wang
# @Email  : wxl1999@foxmail.com

# UPDATE:
# @Time   : 2020/12/17
# @Author : Xiaolei Wang
# @Email  : wxl1999@foxmail.com

from loguru import logger

from crslab.evaluator.base_evaluator import BaseEvaluator
from crslab.evaluator.utils import nice_report
from .metrics import *


class RecEvaluator(BaseEvaluator):
    """The evaluator specially for reommender model
    
    Args:
        rec_metrics: the metrics to evaluate recommender model, including hit@K, ndcg@K and mrr@K
        optim_metrics: the metrics to optimize in training
    """
    def __init__(self):
        super(RecEvaluator, self).__init__()
        self.rec_metrics = Metrics()
        self.optim_metrics = Metrics()

    def rec_evaluate(self, ranks, label):
        for k in [1, 10, 50]:
            if len(ranks) >= k:
                self.rec_metrics.add(f"hit@{k}", HitMetric.compute(ranks, label, k))
                self.rec_metrics.add(f"ndcg@{k}", NDCGMetric.compute(ranks, label, k))
                self.rec_metrics.add(f"mrr@{k}", MRRMetric.compute(ranks, label, k))

    def report(self):
        reports = [self.rec_metrics.report(), self.optim_metrics.report()]
        logger.info('\n' + nice_report(aggregate_unnamed_reports(reports)))

    def reset_metrics(self):
        self.rec_metrics.clear()
        self.optim_metrics.clear()
