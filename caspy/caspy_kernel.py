import traceback
from ipykernel.kernelbase import Kernel
from caspy.parsing import parser
from caspy.printing import latex_numeric
from IPython.display import display, Math

class CaspyKernel(Kernel):
    implementation = "Caspy"
    implementation_version = "0.1"
    language = "python" # Syntax highlighting purposes
    language_version = "3.0"
    language_info = {
        "name": "caspy",
        "mimetype": "text/plain",
        "extension": ".txt"
    }
    banner = "Simple Python CAS"

    def do_execute(self, code, silent, store_history=True,
                   user_expressions=None, allow_stdin=False):
        parser_cls = parser.Parser()
        try:
            num_result = parser_cls.parse(code)
        except Exception as e:
            self.send_response(self.iopub_socket, 'stream', {"name": "stderr", "text": traceback.format_exc()})
            return {
                "status": "error",
                "execution_count": self.execution_count,
                "traceback": [],
                "ename": "",
                "evalue": str(e)
            }

        if not silent:
            latex_str = latex_numeric.latex_numeric_str(num_result)
            self.send_response(self.iopub_socket,"display_data", {
                "data": {
                    "text/latex": "${}$".format(latex_str),
                    "text/plain": latex_str
                }})

        return {"status": "ok",
                "execution_count": self.execution_count,
                "payload": [],
                "user_expressions": []
                }

if __name__ == '__main__':
    from ipykernel.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(
        kernel_class=CaspyKernel)
