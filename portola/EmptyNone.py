def transfer_empty_to_none(field_names, data):
    for field_name in field_names:
        if field_name in data and data[field_name] == "":
            data[field_name] = None
    return data


class TransferEmptyNoneMixin(object):
    def create(self, request):
        print('EmptyToNone')
        if self.empty_to_none_fields:
            transfer_empty_to_none(self.empty_to_none_fields, request.data)
        return super(TransferEmptyNoneMixin, self).create(request)

    def update(self, request, *args, **kwargs):
        if self.empty_to_none_fields:
            transfer_empty_to_none(self.empty_to_none_fields, request.data)
        return super(TransferEmptyNoneMixin, self).update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        if self.empty_to_none_fields:
            transfer_empty_to_none(self.empty_to_none_fields, request.data)
        return super(TransferEmptyNoneMixin, self).partial_update(request, *args, **kwargs)
