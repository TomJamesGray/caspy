class LarkTransformerHelper:
    def unpack_args(self, x):
        """
        Unpacks *args sent by lark
        :param x: The args paramater
        :return:
        """
        for val in x[0].children:
            if len(val.children) > 1:
                yield tuple([x for x in val.children])
            else:
                yield val.children[0]
