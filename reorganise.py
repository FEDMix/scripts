import json
import argparse


def create_argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=argparse.FileType('r'))
    parser.add_argument("-o", "--outfile", type=str, nargs="?")
    return parser


def do_reorganisation(data):
    """
        Takes the one json format and reorganises it so it works
        with the observable notebook.
    """
    result = {'metadata': {}, 'cases': {}}
    # Add all the scans and groun truth data to the cases
    for key, value in sorted(data['scans'].items()):
        case = {
            # Removing duplicates from scans
            'scans': list(dict.fromkeys(value)),
            'ground_truth_masks': data['ground_truth_masks'][key],
        }
        result['cases'][key] = case

    # Add the metrics per patient per algorithm to the json
    for algorithm, metrics in sorted(data['metrics'].items()):
        for metric, patients in metrics.items():
            for patient, values in patients.items():
                if patient in result['cases']:
                    if 'algorithms' not in result['cases'][patient]:
                        result['cases'][patient]['algorithms'] = {}
                    if algorithm not in result['cases'][patient]['algorithms']:
                        result['cases'][patient]['algorithms'][algorithm] = {}
                    if 'metrics' not in result['cases'][patient]['algorithms'][
                            algorithm]:
                        result['cases'][patient]['algorithms'][algorithm][
                            'metrics'] = {}
                    result['cases'][patient]['algorithms'][algorithm][
                        'metrics'][metric] = values

    result['metadata'] = {}
    result['metadata']['clusters'] = []
    # Add the cluster metadata and predicted masks per patient per algorithm
    for algorithm, patients in data['clusters'].items():
        mask_id = 'predicted_masks_' + algorithm
        for patient, predicted_masks in data[mask_id].items():
            result['cases'][patient]['algorithms'][algorithm][
                'predicted_masks'] = predicted_masks
        result['metadata']['clusters'].append({
            'name': algorithm,
            'patients': patients
        })

    return result


if __name__ == "__main__":
    parser = create_argument_parser()
    args = parser.parse_args()

    print(args)
    data = json.load(args.file)

    if args.outfile:
        with open(args.outfile, 'w') as out:
            json.dump(do_reorganisation(data), out, indent=4)
    else:
        print(json.dumps(do_reorganisation(data), indent=4))
