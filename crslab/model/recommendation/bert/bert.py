# @Time   : 2020/12/16
# @Author : Yuanhang Zhou
# @Email  : sdzyh002@gmail.com

# UPDATE
# @Time   : 2020/12/29, 2021/1/4
# @Author : Xiaolei Wang, Yuanhang Zhou
# @email  : wxl1999@foxmail.com, sdzyh002@gmail.com

import os

from loguru import logger
from torch import nn
from transformers import BertModel

from crslab.config import MODEL_PATH
from crslab.data import dataset_language_map
from crslab.model.base_model import BaseModel
from .resource import resources


class BERTModel(BaseModel):
    """The model was proposed in BERT: pre-training of deep bidirectional transformers for language understanding.

    Attributes:
        item_size: A integer indicating the number of items
    """
    def __init__(self, opt, device, vocab, side_data):
        """

        Args:
            opt (dict): A dictionary record the hyper parameters
            device (torch.device): A variable indicating which device to place the data and model
            vocab (dict): A dictionary record the vocabulary information
            side_data (dict): A dictionary record the side data
        """
        self.item_size = vocab['n_entity']

        language = dataset_language_map[opt['dataset']]
        dpath = os.path.join(MODEL_PATH, "tgredial", language)
        resource = resources[language]
        super(BERTModel, self).__init__(opt, device, dpath, resource)

    def build_model(self):
        # build BERT layer, give the architecture, load pretrained parameters
        self.bert = BertModel.from_pretrained(os.path.join(self.dpath, 'bert'))
        # print(self.item_size)
        self.bert_hidden_size = self.bert.config.hidden_size
        self.mlp = nn.Linear(self.bert_hidden_size, self.item_size)

        # this loss may conduct to some weakness
        self.rec_loss = nn.CrossEntropyLoss()

        logger.debug('[Finish build rec layer]')

    def recommend(self, batch, mode='train'):
        context, mask, input_ids, target_pos, input_mask, sample_negs, y = batch

        bert_embed = self.bert(context, attention_mask=mask).pooler_output

        rec_scores = self.mlp(bert_embed)  # bs, item_size

        rec_loss = self.rec_loss(rec_scores, y)

        return rec_loss, rec_scores
