"""IR/라만 귀속용 링커 분자를 3차원으로 만든다.

[왜 링커 단위로 계산하나]
    GFN2-xTB 는 분자 계산입니다(주기 경계는 GFN0/GFN-FF 쪽). 그런데 우리가
    실험과 대조하려는 것은 **작용기의 표지 밴드**이고, C≡N 신축이나 NO₂
    신축은 치환기에 국재된 모드라 금속 배위로 크게 움직이지 않습니다.
    따라서 링커 단위 계산으로 "어느 봉우리가 어느 작용기인가"를 정하는 데는
    충분하고, 금속-질소 영역만 따로 다뤄야 합니다.

[중성형과 음이온형을 둘 다 만드는 이유]
    협력 랩이 손에 쥐는 것은 **중성 이미다졸 전구체**(2-메틸이미다졸 등)이고,
    합성 후 골격 안에 들어가면 **이미다졸레이트 음이온**이 됩니다.
    두 스펙트럼을 다 주면 "전구체가 남아 있는가" 와 "정말 들어갔는가" 를
    같은 자료로 구별할 수 있습니다. N-H 신축(~3100~3400)의 소멸이 그 지표입니다.

[전하]
    이미다졸레이트 음이온은 -1 입니다. 니트로기는 자체가 중성(N⁺-O⁻)이므로
    nIm 음이온도 전체 -1 입니다. xtb 에 --chrg 로 넘겨야 하며, 틀리면
    전자 수가 달라져 진동수가 통째로 어긋납니다.
"""
import json
import os
import sys

from rdkit import Chem
from rdkit.Chem import AllChem

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'spectra', 'xyz')

# (이름, SMILES, 전하, 설명)
MOLS = [
    ('mIm_neutral',  'Cc1ncc[nH]1',                  0,  '2-메틸이미다졸 (전구체)'),
    ('mIm_anion',    'Cc1ncc[n-]1',                 -1,  '2-메틸이미다졸레이트 (골격 내)'),
    ('cnIm_neutral', 'N#Cc1ncc[nH]1',                0,  '2-시아노이미다졸 (전구체)'),
    ('cnIm_anion',   'N#Cc1ncc[n-]1',               -1,  '2-시아노이미다졸레이트'),
    ('nIm_neutral',  'O=[N+]([O-])c1ncc[nH]1',       0,  '2-나이트로이미다졸 (전구체)'),
    ('nIm_anion',    'O=[N+]([O-])c1ncc[n-]1',      -1,  '2-나이트로이미다졸레이트'),
]


def main():
    os.makedirs(OUT, exist_ok=True)
    index = []
    for name, smi, chrg, desc in MOLS:
        m = Chem.MolFromSmiles(smi)
        if m is None:
            print(f'  !! SMILES 실패 {name}: {smi}')
            continue
        m = Chem.AddHs(m)
        if AllChem.EmbedMolecule(m, randomSeed=0xC0FFEE) != 0:
            print(f'  !! 임베딩 실패 {name}')
            continue
        AllChem.MMFFOptimizeMolecule(m, maxIters=2000)
        conf = m.GetConformer()
        path = os.path.join(OUT, f'{name}.xyz')
        with open(path, 'w') as f:
            f.write(f'{m.GetNumAtoms()}\n{name} charge={chrg} {desc}\n')
            for k, at in enumerate(m.GetAtoms()):
                p = conf.GetAtomPosition(k)
                f.write(f'{at.GetSymbol():<3} {p.x:14.8f} {p.y:14.8f} {p.z:14.8f}\n')
        # 전하 검산 -- SMILES 형식전하의 합이 우리가 넘길 값과 같아야 한다
        fc = sum(a.GetFormalCharge() for a in m.GetAtoms())
        flag = '' if fc == chrg else f'  <<< 형식전하 합 {fc} != {chrg}'
        print(f'  {name:<14} 원자 {m.GetNumAtoms():>2}  전하 {chrg:>2}  {desc}{flag}')
        index.append({'name': name, 'smiles': smi, 'charge': chrg,
                      'n_atoms': m.GetNumAtoms(), 'desc': desc, 'xyz': path})
    with open(os.path.join(HERE, 'spectra', 'linker_index.json'), 'w',
              encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=1)
    print(f'\n  {len(index)}개 기록 -> {OUT}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
