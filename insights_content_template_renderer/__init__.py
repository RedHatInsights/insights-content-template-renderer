from js2py.constructors.jsobject import Object

def patch_js2py():
    """Patching js2py for CVE-2024-28397"""
    fn = Object.own["getOwnPropertyNames"]["value"].code
    def wraps(*args, **kwargs):
        result = fn(*args, **kwargs)
        return list(result)
    Object.own["getOwnPropertyNames"]["value"].code = wraps

# Apply the patch on import of this file
patch_js2py()