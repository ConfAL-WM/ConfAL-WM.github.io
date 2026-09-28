#!/usr/bin/env python3
"""Build chapter 06 and insert the paper's seed-42 Oracle reference.

Source: supplied ConfAL-WM manuscript, Table 2 (p.9), Tables 9-11 (pp.24-25),
Tables 13-14 (pp.29-30). Aggregation follows Section 4.3 (p.8).
Figure exports are produced separately by export_appendix_figures.py.
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def figure(title, source, explanation, image_id="", caption_id=""):
    image_attr = f' id="{image_id}"' if image_id else ""
    caption_attr = f' id="{caption_id}"' if caption_id else ""
    return (f'<figure class="eval-fig"><a href="{source}" target="_blank" rel="noopener" '
            f'title="Open full-resolution figure"><img{image_attr} src="{source}" '
            f'alt="{html.escape(title)}" loading="lazy"></a><figcaption{caption_attr}>'
            f'<strong>{title}</strong><span>{explanation}</span></figcaption></figure>')


def pair(*figures, extra=""):
    return f'<div class="eval-figure-row {extra}">' + "\n".join(figures) + '</div>'


def table(number, title, headers, rows, explanation, highlights=None):
    highlights = highlights or set()
    out = [f'<figure class="experiment-result" id="experiment-table-{number}">',
           '<div class="experiment-table" tabindex="0" role="region" '
           f'aria-label="Table {number}: {title}; scroll horizontally for all columns">',
           f'<table class="data-table"><caption>Table {number} · {title}</caption><thead><tr>']
    out += [f'<th scope="col">{h}</th>' for h in headers]
    out.append('</tr></thead><tbody>')
    for ri, row in enumerate(rows):
        out.append('<tr>')
        for ci, value in enumerate(row):
            cls = ' class="experiment-best"' if (ri, ci) in highlights else ''
            out.append(f'<td{cls}>{value}</td>')
        out.append('</tr>')
    out.append(f'</tbody></table></div><figcaption>{explanation}</figcaption></figure>')
    return ''.join(out)


def best(rows, columns, groups=None):
    marked = set()
    for group in groups or [list(range(len(rows)))]:
        for column, higher in columns.items():
            optimum = (max if higher else min)(float(rows[i][column]) for i in group)
            marked.update((i, column) for i in group if float(rows[i][column]) == optimum)
    return marked


def subviews(prefix, views):
    tabs, panels = [], []
    for i, (key, label, content) in enumerate(views):
        tabid, panelid = f'{prefix}-{key}-tab', f'{prefix}-{key}'
        tabs.append(f'<button type="button" class="eval-tab{" active" if i == 0 else ""}" '
                    f'id="{tabid}" role="tab" aria-selected="{str(i == 0).lower()}" '
                    f'aria-controls="{panelid}" tabindex="{0 if i == 0 else -1}">{label}</button>')
        panels.append(f'<div class="eval-view" id="{panelid}" role="tabpanel" '
                      f'aria-labelledby="{tabid}"{ " hidden" if i else ""}>{content}</div>')
    return ('<div class="eval-shell card"><div class="eval-tabs" role="tablist" '
            f'aria-label="{prefix.title()} views" aria-orientation="vertical">' + '\n'.join(tabs) +
            '</div><div class="eval-display">' + '\n'.join(panels) + '</div></div>')


def chapter():
    old = 'assets/confidence_eval/'
    new = 'assets/experiments/'
    why = subviews('diagnostics', [
        ('signal', 'Signal validity', pair(
            figure('High-error detection', old+'signal_auroc_auprc.webp',
                   'Risk is used to find the patches with the largest prediction errors. It performs above chance in latent and pixel space; for the top 5% latent-error patches, AUROC reaches 0.761.'),
            figure('Task-level risk and error', old+'signal_traj_scatter.webp',
                   'Each point compares a task’s average risk with its average prediction error. Higher risk generally means larger error, with a stronger relationship in latent space (Spearman ≈ 0.60) than in pixels (≈ 0.30).'),
            extra='eval-ratio-signal')),
        ('reliability', 'Calibration · Reliability <span class="eval-tab-hint">latent / pixel</span>',
            '<div class="eval-view-bar"><button class="ctrl space-toggle" id="relSpace" type="button">Latent ⇄ Pixel</button></div>' +
            figure('Reliability across thresholds · latent', old+'reliability_sweep_latent.webp',
                   'These plots compare predicted confidence with how often predictions are actually correct. Looser error cutoffs bring the curves closer to the diagonal, but the probe remains overconfident near the main latent-space operating point.', 'relImage', 'relCaption')),
        ('ece', 'Calibration · ECE / Brier', pair(
            figure('Latent-space calibration', old+'ece_brier_tau_latent.webp',
                   'The confidence maps stay fixed while the definition of a correct prediction becomes more permissive. ECE and Brier improve with a looser error cutoff, so calibration depends on the chosen definition of correctness.'),
            figure('Pixel-space calibration', old+'ece_brier_tau_pixel.webp',
                   'The same test is repeated using pixel errors, with better calibration at the selected pixel-space cutoff. Its scores are not directly comparable with latent-space scores because the error scales differ.'))),
        ('tau', 'Sensitivity · probe θ', pair(
            figure('Localization versus probe threshold', old+'probe_tau_localization.webp',
                   'The probe’s conditioning threshold is varied and the risk maps are regenerated. Low-to-moderate thresholds preserve the strongest error localization; large thresholds make patches look similarly confident.'),
            figure('Calibration versus probe threshold', old+'probe_tau_calibration.webp',
                   'Increasing the conditioning threshold raises mean confidence, but does not consistently improve ECE or Brier. A more confident prediction is not necessarily a better-calibrated one.'), extra='eval-ratio-62-35')),
    ])
    rows9 = [
        ['Bottleneck','Tuned fixed','0.089487','0.288859','0.00567','0.78379'],
        ['Bottleneck','EMA','0.089551','0.289220','0.00639','0.78487'],
        ['Decoder','Tuned fixed','0.084181','0.271915','0.00402','0.82237'],
        ['Decoder','EMA','0.084243','0.272314','0.00643','0.82184'],
    ]
    t9 = table(9, 'Feature and supervision comparison',
        ['Feature','Supervision','Brier ↓','BCE ↓','ECE ↓','AUROC ↑'], rows9,
        'With the same probe size and training setup, decoder features reduce Brier by about 5.93% compared with bottleneck features. EMA and calibrated fixed thresholds perform similarly, with tuned fixed slightly ahead for decoder features.',
        best(rows9, {2:False,3:False,4:False,5:True}))
    ranges = ['Fixed [0.20, 0.70]','Fixed [Q<sub>.10</sub>, Q<sub>.90</sub>]',
              'Fixed [Q<sub>.05</sub>, Q<sub>.95</sub>] †','Fixed [Q<sub>.20</sub>, Q<sub>.80</sub>]','EMA','EMA-Qinit']
    values10 = [
        ['0.154102','0.153483','0.12854','0.77596','0.090326'],
        ['0.092173','0.089468','0.00670','0.78338','0.057385'],
        ['0.092149','0.089487','0.00567','0.78379','0.057210'],
        ['0.092776','0.090206','0.01182','0.78185','0.058627'],
        ['0.092239','0.089551','0.00639','0.78487','0.057544'],
        ['0.092101','0.089477','0.00694','0.78517','0.057503'],
        ['0.133136','0.133257','0.10630','0.81088','0.085256'],
        ['0.086885','0.084235','0.00617','0.82313','0.054462'],
        ['0.086872','0.084181','0.00402','0.82237','0.054344'],
        ['0.087667','0.085248','0.01142','0.82040','0.056637'],
        ['0.086867','0.084243','0.00643','0.82184','0.054400'],
        ['0.086840','0.084266','0.00548','0.82235','0.054522'],
    ]
    rows10 = [['Bottleneck' if i<6 else 'Decoder', ranges[i%6], *v] for i,v in enumerate(values10)]
    t10 = table(10, 'Complete threshold-range ablation',
        ['Feature','Supervision','Cal. Brier ↓','Test Brier ↓','Test ECE ↓','Test AUROC ↑','Low-noise Brier ↓'], rows10,
        'All 12 fits compare manually chosen, training-quantile, and adaptive threshold ranges. Quantile-based ranges and EMA are much stronger than [0.20, 0.70]; † marks the fixed range selected using calibration data.',
        best(rows10, {2:False,3:False,4:False,5:True,6:False}, [list(range(6)),list(range(6,12))]))
    rows11 = [
        ['Decoder − bottleneck (fixed)','−5.331','[−5.657, −4.987]','−2.767','[−3.156, −2.243]'],
        ['Decoder − bottleneck (EMA)','−5.294','[−5.637, −4.934]','−3.141','[−3.475, −2.762]'],
        ['EMA − fixed (decoder)','+0.072','[+0.011, +0.134]','−0.016','[−0.151, +0.091]'],
        ['EMA − fixed (bottleneck)','+0.035','[−0.071, +0.143]','+0.358','[+0.270, +0.449]'],
        ['Feature × supervision','+0.037','[−0.090, +0.170]','−0.374','[−0.562, −0.229]'],
    ]
    t11 = table(11, 'Paired task-level Brier differences (×10³)',
        ['Contrast','Training noise · Δ','Training noise · 95% CI','Low noise · Δ','Low noise · 95% CI'],rows11,
        'Each task receives equal weight, and the 95% intervals come from 3,000 task-bootstrap resamples at seed 42; negative differences favor the first named configuration. Decoder gains remain clear in both noise ranges, while EMA-versus-fixed differences are much smaller.')
    ablations = subviews('ablations', [
        ('features','Feature comparison',t9 + figure('Figure 15 · Shared-threshold performance',new+'fig15-shared-thresholds.webp',
            'All four probes answer the same nine error thresholds. Fixed and EMA curves nearly overlap, while changing from bottleneck to decoder features produces the larger improvement.')),
        ('ranges','Threshold ranges',t10 + '<p class="experiment-footnote">Q denotes a training-error quantile. EMA-Qinit starts at [Q<sub>.10</sub>, Q<sub>.90</sub>]; green cells mark the best value within each feature group.</p>'),
        ('paired','Paired task comparisons',t11 + figure('Figure 16 · Feature and supervision effects',new+'fig16-paired-effects.webp',
            'The error bars compare paired Brier differences across held-out tasks. Decoder features show a much larger benefit than the difference between EMA and tuned fixed supervision; the two panels use different horizontal scales.')),
        ('noise','Noise-range transfer',figure('Figure 17 · Evaluation at lower noise',new+'fig17-noise-transfer.webp',
            'The same trained probes are evaluated at training-range and lower noise levels. Decoder features keep their Brier advantage, but lower Brier comes with higher ECE because the error distribution and target balance change.')),
        ('alignment','Error alignment',figure('Figure 18 · Do weights emphasize real errors?',new+'fig18-error-alignment.webp',
            'Patch weights and frame risk are compared with actual latent errors before world-model retraining. Decoder features align more strongly with errors under both supervision rules, and this advantage survives the weighting transformation.')),
        ('qualitative','Qualitative comparison',figure('Figure 19 · Two held-out hammering episodes',new+'fig19-qualitative.webp',
            'Ground-truth frames and error maps are shown beside the four probe responses. Decoder features preserve finer spatial detail, while EMA and tuned fixed supervision produce similar patterns for the same features.')),
        ('ema','EMA threshold',pair(
            figure('EMA threshold · full run',old+'ema_threshold.webp',
                'The lower and upper supervision thresholds adapt to the observed training-error scale. After the early adjustment, the sampling band stays relatively stable instead of remaining at its initial range.'),
            figure('EMA threshold · warmup zoom',old+'ema_threshold_zoom.webp',
                'The first 100 updates show how quickly EMA moves away from its starting bounds. The band settles early, so subsequent thresholds are sampled on a scale that better matches the training errors.'))),
    ])
    rows13 = [
        ['10%','Random','1,824','0.6341','0.8772','0.5007','0.1701','4.47'],
        ['10%','Confidence','1,824','0.6995','0.9088','0.5900','0.2502','4.45'],
        ['20%','Random','3,649','0.6679','0.9003','0.5391','0.2360','4.45'],
        ['20%','Confidence','3,649','0.6642','0.8812','0.6167','0.1970','4.44'],
        ['40%','Random','7,298','0.6874','0.8786','0.5576','0.2004','4.44'],
        ['40%','Confidence','7,298','0.6611','0.8981','0.5987','0.2305','4.47'],
        ['100%','Full pool','18,244','0.6902','0.9030','0.5263','0.2023','4.46'],
    ]
    t13 = table(13,'Budget sensitivity under 750 updates',
        ['Budget','Selection','Episodes','Reconstruction ↑','Scene ↑','Semantics ↑','Motion ↑','Train GPU-h'],rows13,
        'With the same 750 updates, confidence beats random on all four aggregate scores at the 10% budget; larger budgets bring metric-dependent trade-offs. Training costs stay around 4.44–4.47 GPU-hours, so selecting fewer episodes does not reduce compute in this experiment.',
        best(rows13,{3:True,4:True,5:True,6:True},[[0,1],[2,3],[4,5]]))
    rows14 = [
        ['10%','+0.0655 [0.0534, 0.0772]','+0.0316 [0.0229, 0.0396]','+0.0914 [0.0247, 0.1563]','+0.0801 [0.0293, 0.1391]'],
        ['20%','−0.0037 [−0.0186, 0.0112]','−0.0190 [−0.0296, −0.0089]','+0.0768 [0.0119, 0.1425]','−0.0389 [−0.1023, 0.0185]'],
        ['40%','−0.0263 [−0.0411, −0.0120]','+0.0195 [0.0031, 0.0362]','+0.0440 [−0.0164, 0.1021]','+0.0301 [−0.0570, 0.1390]'],
    ]
    t14 = table(14,'Confidence minus random · paired mean [95% CI]',
        ['Budget','Δ Reconstruction ↑','Δ Scene ↑','Δ Semantics ↑','Δ Motion ↑'],rows14,
        'Paired episode comparisons show confidence’s clearest advantage at 10%: all four intervals lie above zero. At 20% and 40%, some intervals cross zero or favor random, so the gain is not uniform across budgets and metrics.')
    budget = subviews('budget',[
        ('curves','Budget–performance curves',figure('Figure 21 · Nine metrics across data budgets',new+'fig21-budget-curves.webp',
            'Confidence and random selection receive the same 750 updates, with the full-pool model shown as a reference. More data does not consistently improve every metric under this short schedule, and confidence’s broadest advantage appears at 10%.')),
        ('results','Aggregate results & cost',t13 + '<p class="experiment-footnote">Green marks the higher score within each confidence/random pair. Reconstruction, Scene and Motion use 62 episodes; CLIP/BLEU use 56, and Semantics averages the available component means.</p>'),
        ('paired','Paired differences',t14 + '<p class="experiment-footnote">10,000 episode-bootstrap resamples. Reconstruction, Scene and Motion use 62 common episodes; Semantics uses the 56-episode intersection, so paired differences can differ slightly from subtracting Table 13.</p>'),
    ])
    chips = ('<div class="metric-chips"><span class="chip">Patch / Frame / Task Spearman <b>0.540 / 0.590 / 0.595</b></span>'
             '<span class="chip">Top-5% patch AUROC <b>0.761</b></span><span class="chip">Adjacent-frame top-region IoU <b>0.740</b></span>'
             '<span class="chip">Risk flicker <b>0.005</b></span><span class="chip">Peak temporal correlation <b>0.602</b></span></div>')
    parts = [
        ('why','Why Confidence?',chips+why),
        ('ablations','Feature &amp; Threshold Ablations',
         '<p class="experiment-protocol">Appendix B.3 · Frozen EVAC-v1, identical probe capacity, 6,000 updates and seed 42. Evaluation uses 250 held-out episodes across 43 tasks; the fixed range is chosen on a separate calibration split.</p>'+ablations),
        ('budget','Data-Budget Sensitivity',
         '<p class="experiment-protocol">Appendix B.5 · 750 updates, effective batch size 16, seed 42 and no loss weighting. Confidence and uniform-task random selection share the quota allocator; a fixed 64-episode validation subset is used, with metric-specific valid counts below.</p>'+budget),
    ]
    buttons, panels = [], []
    for i,(key,label,content) in enumerate(parts):
        buttons.append(f'<button class="experiment-tab{" active" if i == 0 else ""}" type="button" '
                       f'role="tab" id="experiment-{key}-tab" aria-controls="experiment-{key}" '
                       f'aria-selected="{str(i == 0).lower()}" tabindex="{0 if i == 0 else -1}">{label}</button>')
        panels.append(f'<div class="experiment-panel" id="experiment-{key}" role="tabpanel" '
                      f'aria-labelledby="experiment-{key}-tab"{" hidden" if i else ""}>{content}</div>')
    return ('<section class="section reveal" id="confidence-eval">\n'
            '<div class="section-head"><div><div class="kicker">06 · More Experiments</div>'
            '<h2>From confidence signals to design choices and data budgets.</h2></div>'
            '<div class="section-note">Explore confidence diagnostics, controlled probe ablations, and fixed-update budget comparisons.</div></div>\n'
            '<div class="experiment-tabs" role="tablist" aria-label="More experiments">'+ '\n'.join(buttons) + '</div>\n' +
            '\n'.join(panels) + '\n</section>')


def main():
    path = ROOT / 'index.html'
    text = path.read_text(encoding='utf-8')
    start = text.index('<section class="section reveal" id="confidence-eval">')
    end = text.index('\n<section class="section reveal" id="resources">',start)
    text = text[:start] + chapter() + '\n' + text[end:]
    match = re.search(r'const PAPER_DATA = (.*?);\n',text)
    data = json.loads(match.group(1))
    metrics = ['psnr','ssim','scene_consistency','logics','semantics_CLIPScore','semantics_BLEUScore','traj_hsd','traj_dyn','traj_ndtw']
    values = [0.6458,0.7542,0.8988,0.5826,0.8875,0.2914,0.0985,0.0587,0.1396]
    base = dict(method='Oracle error',weighting='None',key='oracle_error',block='selection')
    oracle = dict(base,**dict(zip(metrics,values)))
    aggregate = dict(base,Reconstruction=(values[0]+values[1])/2,Scene=values[2],
                     Semantics=sum(values[3:6])/3,Motion=sum(values[6:9]))
    for kind,row in [('detailed',oracle),('aggregated',aggregate)]:
        for seed,rows in data[kind].items():
            rows[:] = [r for r in rows if r['key'] != 'oracle_error']
            rows.insert(next(i for i,r in enumerate(rows) if r['key']=='random')+1,row.copy())
    text = text[:match.start(1)] + json.dumps(data,separators=(',',':'),ensure_ascii=True) + text[match.end(1):]
    path.write_text(text,encoding='utf-8',newline='\n')
    print('Updated chapter 06 and Oracle reference in all eight result-table views.')


if __name__ == '__main__':
    main()
