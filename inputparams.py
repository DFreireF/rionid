class InputParams():
    def __init__(self, filename):
        self._read(filename)

    def _read(self,filename):
        self.dict = {k: (float(v) if v.replace('.', '').isdigit() else v)
                     for k, v in [line.split() for line in open(filename)]}
        self.lisefile = self.dict['lise_filename']

def test1():
    params_file = 'data/InputParameters.txt'
    parameter_dict = InputParams(params_file)
    print(f'Dictionary Created from {params_file}')
    for key,value in parameter_dict.dict.items():
        print(f'{key} = {value}')
    print(f'lise filename can be found using self.lisefile')


if __name__ == '__main__':
    try:
        test1()
    except:
        raise
