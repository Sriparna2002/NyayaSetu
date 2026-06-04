from django.shortcuts import redirect

# ******* Authenticated *******
def auth(view_function):
    def wrapped_view(request,*args,**kwargs):
        if request.user.is_authenticated == False:
            return redirect('admin_login')
        return view_function(request, *args, **kwargs)
    return wrapped_view

# ******* Guest *******
def guest(view_function):
    def wrapped_view(request,*args,**kwargs):
        if request.user.is_authenticated:
            return redirect('admin_dashboard')
        return view_function(request, *args, **kwargs)
    return wrapped_view