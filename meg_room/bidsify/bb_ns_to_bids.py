'''
Code from Richard
'''



from pathlib import Path
import json
import shutil
from tempfile import TemporaryDirectory
import subprocess

import pandas as pd
import questionary
import numpy as np
import mne
import mne_bids

from aa_create_config import Config


mne.set_log_level('error')


event_id_orig = {
    'trial_start': 1,
    'feedback': 29,
    'trial_end': 30,
    'missing_response': 66,

    # Stimulation
    'stim/1': 11,
    'stim/2': 12,
    'stim/3': 13,
    'stim/4': 14,

    # Rhythmic reaction time measurement
    'stim/rt_meas': 90,

    # Responses
    'response/onset': 2048,
    'response/offset/1': 21,
    'response/offset/2': 22,
    'response/offset/3': 23,
    'response/offset/4': 24,

    # Retention period onset
    'rp_on/1_item/short': 110,
    'rp_on/1_item/medium': 120,
    'rp_on/1_item/long': 130,

    'rp_on/3_item/short/1': 211,
    'rp_on/3_item/short/2': 212,
    'rp_on/3_item/short/3': 213,
    'rp_on/3_item/short/4': 214,
    'rp_on/3_item/short/5': 215,
    'rp_on/3_item/short/6': 216,

    'rp_on/3_item/medium/1': 221,
    'rp_on/3_item/medium/2': 222,
    'rp_on/3_item/medium/3': 223,
    'rp_on/3_item/medium/4': 224,
    'rp_on/3_item/medium/5': 225,
    'rp_on/3_item/medium/6': 226,

    'rp_on/3_item/long/1': 231,
    'rp_on/3_item/long/2': 232,
    'rp_on/3_item/long/3': 233,
    'rp_on/3_item/long/4': 234,
    'rp_on/3_item/long/5': 235,
    'rp_on/3_item/long/6': 236
}

stim_channel = 'STI101'
min_event_duration = 0.005

default_out_dir = Path('/neurospin/meg/meg_tmp/TimeInWM_Izem_2019/BIDS')


def main():
    config_path = questionary.path(
        message='Path to the config JSON file?',
        default='/neurospin/meg/meg_tmp/TimeInWM_Izem_2019/scripts/convert_to_bids/configs/bids_conversion_config.json',
        file_filter=lambda x: Path(x).suffix == '.json',
        validate=lambda x: Path(x).exists()
    ).ask()

    if config_path is None:
        return
    config_path = Path(config_path)

    out_dir = questionary.path(
        message='Output directory',
        default=str(default_out_dir),
        file_filter=lambda x: Path(x).is_dir()
    ).ask()
    if out_dir is None:
        return
    out_dir = Path(out_dir)

    if out_dir.exists():
        rmdir = questionary.confirm(
            message='Output directory exists. Delete it before proceeding?',
            default=False
        ).ask()
        if rmdir:
            rmdir = questionary.confirm(
                message='Are you absolutely sure?',
                default=False
            ).ask()
            if rmdir:
                shutil.rmtree(out_dir)

    out_dir.mkdir(exist_ok=True)

    which_data_choices = [
        questionary.Choice(title='MEG', value='meg', checked=True),
        questionary.Choice(title='T1 MRI', value='t1', checked=True)
    ]

    which_data = questionary.checkbox(
        message='Which data would you like to convert to BIDS?',
        choices=which_data_choices,
        validate=lambda x: len(x) > 0
    ).ask()
    if which_data is None:
        return

    with config_path.open('r', encoding='utf-8') as f:
        config: Config = json.load(f)

    anonymize_data = config['anonymization']['anonymize']
    daysback = config['anonymization']['daysback']
    symlink = True if not anonymize_data else False
    
    ct_path =  Path(config['meg']['crosstalk_path'])
    cal_path = Path(config['meg']['finecal_path'])

    bids_root = out_dir
    bids_path = mne_bids.BIDSPath(datatype='meg', suffix='meg', root=bids_root,
                                  extension='.fif')

    subject_choices = []
    for subject in config['subjects']:
        subject_id = subject['id']
        subject_id_anonymized = subject['anonymized_id']
        choice = questionary.Choice(
            title=f'{subject_id} [anonymized id: {subject_id_anonymized}]',
            value=subject_id
        )
        subject_choices.append(choice)

    subjects = questionary.checkbox(
        message='Which subjects would you like to process?',
        choices=subject_choices,
        validate=lambda x: len(x) > 0
    ).ask()
    if subjects is None:
        return

    for sub_config in config['subjects']:
        if sub_config['id'] not in subjects:
            print(f'Skipping deselected participant {sub_config["id"]}.')
            continue

        print(f'Processing participant: {sub_config["id"]} … ')
        if anonymize_data:
            sub_id = sub_config['anonymized_id']
            anonymize = dict(daysback=daysback, keep_his=False)
        else:
            sub_id = sub_config['id'].replace('_', '')
            anonymize = None

        if 'meg' in which_data:
            # Empty-room recording
            er_path = Path(sub_config['empty_room_path'])
            er_session = sub_config['empty_room_session']

            raw = mne.io.read_raw_fif(er_path, allow_maxshield=True)
            raw.set_meas_date(er_session)

            bids_path_er = (bids_path.copy()
                            .update(subject='emptyroom', task='noise',
                                    session=er_session))
            bids_path_er = mne_bids.write_raw_bids(
                raw, bids_path=bids_path_er,
                anonymize=anonymize,
                symlink=symlink, overwrite=True
            )

            # Resting-state
            rest_path = Path(sub_config['rest_path'])
            raw = mne.io.read_raw_fif(rest_path, allow_maxshield=True)
            bids_path_rest = (bids_path.copy()
                            .update(subject=sub_id, task='rest'))
            mne_bids.write_raw_bids(
                raw, bids_path=bids_path_rest,
                empty_room=bids_path_er,
                anonymize=anonymize,
                symlink=symlink, overwrite=True
            )

            # Task runs
            for task_config in sub_config['tasks']:
                task_name = task_config['name']
                run_paths = task_config['paths']
                bads = task_config['bads']

                for run_idx, (run_path, run_bads) in enumerate(
                    zip(run_paths, bads),
                    start=1
                ):
                    print(f'Run {run_idx} …')
                    raw = mne.io.read_raw_fif(
                        run_path, allow_maxshield='yes', verbose='error'
                    )
                    raw.info['bads'] = run_bads

                    events = mne.find_events(
                        raw=raw,
                        consecutive=True,
                        shortest_event=1
                    )
                    idx_keep = np.where(
                        (events[:, -1] != 2080) &
                        (events[:, -1] != 2069) &
                        (events[:, -1] != 2070) &
                        (events[:, -1] != 2071) &
                        (events[:, -1] != 2072)
                    )[0]
                    events_cleaned = events[idx_keep]

                    events_to_drop = []
                    first_trial_start_idx = np.where(
                        events_cleaned[:, -1] == 1  # Trigger 1 -> First trial
                    )[0][0]

                    for idx, event in enumerate(
                        events_cleaned[first_trial_start_idx:],
                        start=first_trial_start_idx
                    ):
                        if idx == 0:
                            continue

                        if event[-1] == events_cleaned[idx - 1, -1] == 2048:
                            assert  events_cleaned[idx + 1, -1] != 2048
                            # if events_cleaned[idx + 1, -1] == 2048:
                            #     print(idx)
                            events_to_drop.append(idx)

                    mask = np.ones(len(events_cleaned), dtype=bool)
                    mask[np.asanyarray(events_to_drop)] = False
                    events_cleaned = events_cleaned[mask]

                    events = events_cleaned
                    # events_regular = mne.find_events(
                    #     raw=raw,
                    #     stim_channel=stim_channel,
                    #     min_duration=min_event_duration
                    # )

                    if sub_id == 'cc150418':
                        bad_events = [
                            2, 83, 84, 85, 86, 87, 88, 93, 94, 95, 96,
                            97, 98, 103, 104, 105, 106, 107, 108
                        ]

                        # for idx, e in enumerate(events_regular[:, 2]):
                        #     if e in bad_events:
                        #         events_regular[idx, 2] += 128
                        for idx, e in enumerate(events[:, 2]):
                            if e in bad_events:
                                events[idx, 2] += 128


                    # events_to_keep_idx = np.array([
                    #     e[-1] in event_id.values()
                    #     for e in events
                    # ])
                    # events_to_drop = events[~events_to_keep_idx, -1]
                    # print(f'Dropping unknown events: {np.unique(events_to_drop)}')
                    # events = events[events_to_keep_idx]

                    # Second pass:
                    # Find button presses (offsets)
                    # events_button_offsets = mne.find_events(
                    #     raw=raw,
                    #     stim_channel=stim_channel,
                    #     shortest_event=1,
                    #     consecutive=True
                    # )
                    # event_button_offset_trigger_codes = (21, 22, 23, 24)
                    # idx_button_offsets = [
                    #     e[-1] in event_button_offset_trigger_codes
                    #     for e in events_button_offsets
                    # ]
                    # events_button_offsets = events_button_offsets[idx_button_offsets]

                    # # Paste it all together …
                    # events = np.vstack(
                    #     [events_regular, events_button_offsets]
                    # )
                    # events = events[np.argsort(events[:, 0])]

                    event_id = event_id_orig.copy()
                    keep_event = np.ones(len(events), dtype=bool)
                    for idx, event in enumerate(events):
                        event_code = event[-1]
                        prev_event_code = event[1]
                        # if event_code in event_button_offset_trigger_codes:
                        #     event[-1] = event_code - 2048

                        if (
                            event_code == 1 and
                            (
                                prev_event_code in [11, 12, 13, 14, 21] or
                                200 < prev_event_code < 300
                            )
                        ):
                            print(
                                '    Omitting spurious trial_start event '
                                'during ongoing trial'
                            )
                            keep_event[idx] = False
                            continue

                        if (
                            event_code in [21, 22, 23, 24] and
                            200 < prev_event_code < 300
                        ):
                            print(
                                '    Omitting spurious response offset event '
                                'immediately after RP start'
                            )
                            keep_event[idx] = False
                            continue

                        if (
                            event_code in [11, 12, 13, 14] and
                            (
                                event_code == prev_event_code + 1 or
                                100 < prev_event_code < 200
                            )
                        ):
                            print(
                                '    Omitting spurious stimulus onset event'
                            )
                            keep_event[idx - 1] = False
                            continue

                        # Remove duplicated feedback trigger
                        if (
                            event_code in [29, 2077] and
                            prev_event_code in [29, 2077]
                        ):
                            print('    Omitting spurious feedback event')
                            keep_event[idx - 1] = False

                        # Remove spurious response offset and stimulus onset
                        # events after feedback has already been provided
                        if (
                            event_code == 30 and
                            prev_event_code == 24
                        ):
                            print('    Omitting spurious response offset '
                                  'event after feedback')
                            keep_event[idx - 1] = False

                        if (
                            event_code == 30 and
                                events[idx - 1, -1] == 13
                        ):
                            print('    Omitting spurious stimulus onset '
                                  'event after feedback')
                            keep_event[idx - 1] = False


                        # Remove responses before beginning of the RP
                        if (
                            (
                                event_code in [11, 12, 13, 14] or
                                100 < event_code < 300
                            ) and
                            events[idx - 1, -1] in [2048, 4096]
                        ):
                            print(
                                '    Omitting spurious response before RP'
                            )
                            keep_event[idx - 1] = False

                        if event_code not in event_id.values():
                            # print(
                            #     f'    Encountered unknown event: {event_code} '
                            #     f'– {event}'
                            # )

                            if (
                                prev_event_code == 2048 and  # Button press
                                event_code > 2048 and
                                event_code - 2048 in event_id_orig.values()
                            ):
                                corrected_event_code = event_code - 2048
                                event[-1] = corrected_event_code
                                print(f'    Correcting event code to: '
                                      f'{corrected_event_code}')
                            elif (
                                prev_event_code == 0 and
                                event_code == 4096  # Button press
                            ):
                                corrected_event_code = 2048
                                event[-1] = corrected_event_code
                                print(f'Correcting event code to: '
                                      f'{corrected_event_code}')
                            elif (
                                prev_event_code == 4096 and  # Button press
                                event_code > 4096 and
                                event_code - 4096 in event_id_orig.values()
                            ):
                                corrected_event_code = event_code - 4096
                                event[-1] = corrected_event_code
                                print(f'Correcting event code to: '
                                      f'{corrected_event_code}')

                            else:
                                assert str(event_code) not in event_id
                                # print(f'Adding {event_code} to event_id dict.')
                                # event_id[str(event_code)] = event_code
                                print(
                                    f'    Omitting unknown event with code: '
                                    f'{event_code}'
                                )
                                keep_event[idx] = False

                    events = events[keep_event]

                    bids_path_task = (
                        bids_path
                        .copy()
                        .update(
                            subject=sub_id, task=task_name,
                            run=run_idx
                        )
                    )

                    bp_written = mne_bids.write_raw_bids(
                        raw=raw,
                        bids_path=bids_path_task,
                        events_data=events,
                        event_id=event_id,
                        empty_room=bids_path_er,
                        anonymize=anonymize,
                        symlink=symlink,
                        overwrite=True
                    )

                    bp_events = bp_written.copy().update(
                        suffix='events', extension='.tsv'
                    )
                    events_tsv = pd.read_csv(
                        bp_events.fpath,
                        sep='\t'
                    )
                    check_events(events=events_tsv)
                    adjust_response_event_naming(events_path=bp_events.fpath)

                    mne_bids.read_raw_bids(bp_written)
                    print('… done')

            # Fine-calibration and crosstalk files
            bids_path_meg_conf= bids_path.copy().update(subject=sub_id)
            mne_bids.write_meg_calibration(calibration=cal_path,
                                        bids_path=bids_path_meg_conf)
            mne_bids.write_meg_crosstalk(fname=ct_path,
                                        bids_path=bids_path_meg_conf)

        # T1 MRI
        if 't1' in which_data:
            t1_dicom_path = Path(sub_config['t1_dicom_path'])
            with TemporaryDirectory() as temp_dir:
                    dcm2niix_params = [
                        '-o', temp_dir,
                        '-f', sub_id,       # filename base
                        '-b', 'y',          # create BIDS sidecar
                        '-d', '0',          # directory search depth
                        '-m', 'y',          # merge 2D slices
                        '-w', '1',          # overwrite existing files
                        '-z', 'y',          # use gzip compression
                        '--progress', 'y',  # show progress bar
                    ]

                    if not anonymize_data:
                        dcm2niix_params += [
                            '-ba', 'n',         # don't anonymize BIDS
                        ]

                    dcm2niix_params += [str(t1_dicom_path)]
                    dcm2niix_cmd = ['dcm2niix'] + dcm2niix_params
                    subprocess.run(dcm2niix_cmd)

                    nii_path_in = Path(temp_dir) / f'{sub_id}.nii.gz'
                    json_path_in = Path(temp_dir) / f'{sub_id}.json'
                    bids_path_t1 = (bids_path.copy()
                                    .update(subject=sub_id,
                                            datatype='anat', suffix='T1w',
                                            extension='.nii.gz'))

                    bids_path_t1 = mne_bids.write_anat(image=nii_path_in,
                                                       bids_path=bids_path_t1,
                                                       overwrite=True)
                    bids_path_t1_json = (bids_path_t1.copy()
                                         .update(extension='.json'))

                    # Enrich the MNE-BIDS-generated sidecar
                    with json_path_in.open('r', encoding='utf-8') as f:
                        json_data_dcm2niix = json.load(f)

                    # BIDS sidecar is only created if fiducial points were
                    # passed
                    if not bids_path_t1_json.fpath.exists():
                        with (bids_path_t1_json.fpath
                                .open('w', encoding='utf-8')) as f:
                            json.dump(dict(), f, indent=2)

                    with (bids_path_t1_json.fpath
                            .open('r', encoding='utf-8')) as f:
                        json_data_mne_bids = json.load(f)

                    updates = dict()
                    for key, value in json_data_dcm2niix.items():
                        if key not in json_data_mne_bids:
                            updates[key] = value

                    mne_bids.update_sidecar_json(bids_path=bids_path_t1_json,
                                                 entries=updates,
                                                 verbose=False)

        print('\n')


def check_events(events: pd.DataFrame):
    trial_starts = events.loc[events['trial_type'] == 'trial_start', :].index
    trial_ends = trial_starts[1:] - 1
    trial_ends = trial_ends.append(pd.Index([events.index[-1]]))

    trial_start_end_events = pd.DataFrame(
        {
            'trial_start_idx': trial_starts,
            'trial_end_idx': trial_ends
        },
        index=pd.Index(range(1, len(trial_starts) + 1), name='trial')
    )

    trial_dfs = []
    for _, trial_idx in trial_start_end_events.iterrows():
        start_idx = trial_idx['trial_start_idx']
        end_idx = trial_idx['trial_end_idx']
        if end_idx == start_idx + 1:
            print('    Omitting spurious trial: only start & end events')
            continue

        trial_df = events.loc[start_idx:end_idx]

        rp_on_idx = (
            trial_df['trial_type']
            .apply(lambda x: x.startswith('rp_on'))
        )
        if rp_on_idx.sum() == 0:
            print('    Omitting spurious trial: no retention period onset trigger')
            continue

        trial_end_event_idx = trial_df['trial_type'] == 'trial_end'
        assert trial_end_event_idx.sum() <= 1
        if trial_end_event_idx.sum():
            idx = trial_df.loc[trial_end_event_idx].index[0]
            if idx != trial_df.index[-1]:
                print(
                    f'    Omitting orphaned event(s):\n'
                    f'    {trial_df.loc[idx + 1:]}')
                trial_df = trial_df.loc[:idx]
                # print(trial_df)

        trial_dfs.append(trial_df)

    print(f'    Found {len(trial_dfs)} trials.')

    for trial_idx, trial in enumerate(trial_dfs, start=1):
        missing_response_idx = trial['trial_type'] == 'missing_response'
        trial_type_1_item_event_idx = (
            trial['trial_type']
            .apply(lambda x: x.startswith('rp_on/1_item'))
        )
        trial_type_3_item_event_idx = (
            trial['trial_type']
            .apply(lambda x: x.startswith('rp_on/3_item'))
        )
        stimulus_onset_idx = (
            trial['trial_type']
            .apply(lambda x: x.startswith('stim'))
        )
        response_onset_idx = trial['trial_type'] == 'response/onset'
        response_offset_idx = (
            trial['trial_type']
            .apply(lambda x: x.startswith('response/offset'))
        )
        feedback_idx = trial['trial_type'] == 'feedback'

        if trial_type_1_item_event_idx.any():
            assert not trial_type_3_item_event_idx.any()
            expected_response_count = expected_stimulus_count = 2
        elif trial_type_3_item_event_idx.any():
            assert not trial_type_1_item_event_idx.any()
            expected_response_count = expected_stimulus_count = 4

        if missing_response_idx.sum() > 0:
            print(f'    Trial {trial_idx}: Missing responses')
            continue

        assert expected_stimulus_count == expected_response_count
        assert stimulus_onset_idx.sum() == expected_stimulus_count
        # We sometimes have spurious (additional) responses – for now, it's
        # okay to keep those! Therefore, we use >= below
        assert response_onset_idx.sum() >= expected_response_count
        if response_onset_idx.sum() > expected_response_count:
            print(
                f'    Trial {trial_idx}: '
                f'Found {response_onset_idx.sum()} responses after beginning '
                f'of RP, expected {expected_response_count}. Keeping all.'
            )
        # For offset events, we never have spurious ones
        assert response_offset_idx.sum() == expected_response_count
        assert feedback_idx.sum() == 1


def adjust_response_event_naming(events_path):
    """
    Number responses within a trial, e.g. go from 2 occurences of
    `response/onset` to `response/onset/1` and `response/onset/2`.
    """
    print('    Assigning distinguishable event names to responses.')
    events_tsv = pd.read_csv(events_path, sep='\t')

    trial_start_idx = events_tsv.loc[events_tsv['trial_type'] == 'trial_start', :].index
    trial_stop_idx = [
        *trial_start_idx[1:] - 1,
        events_tsv.index[-1]
    ]
    for start_idx, stop_idx in zip(trial_start_idx, trial_stop_idx):
        trial_events = events_tsv.loc[start_idx:stop_idx]
        onset_events = trial_events.loc[trial_events['trial_type'] == 'response/onset', :]
        
        onset_event_names = [f'response/onset/{i+1}'
                            for i in range(
                                len(onset_events.index)
                            )]
        onset_event_codes = [5000 + i + 1
                            for i in range(
                                len(onset_events.index)
                            )]

        events_tsv.loc[onset_events.index, 'trial_type'] = onset_event_names
        events_tsv.loc[onset_events.index, 'value'] = onset_event_codes
        events_tsv.to_csv(events_path, sep='\t', encoding='utf-8-sig')


if __name__ == '__main__':
    main()
