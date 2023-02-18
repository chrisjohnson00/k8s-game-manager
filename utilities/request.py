def get_unknown_params(known_params, request):
    unknown_params = []
    for param_name in request.form:
        if param_name not in known_params:
            param_value = request.form[param_name]
            unknown_params.append({'key': param_name, 'value': param_value})
    return unknown_params
