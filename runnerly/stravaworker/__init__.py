from stravalib import Client
import requests

#from celery import Celery
#BACKEND = BROKER = 'redis://localhost:6379'
#celery = Celery(__name__, backend=BACKEND, broker=BROKER)

DATASERVICE = 'http://127.0.0.1:5002'


def fetch_all_runs():
    users = requests.get(DATASERVICE + '/users').json()['users']
    runs_fetched = {}

    for user in users:
        strava_token = user.get('strava_token')
        email = user['email']

        if strava_token is None:
            continue

        print('Fetching Strava for %s' % email)
        runs_fetched[user['id']] = fetch_runs(user)

    return runs_fetched


def push_to_dataservice(runs):
    requests.post(DATASERVICE + '/add_runs', json=runs)


def activity2run(activity):
    """Used by fetch_runs to convert a strava entry.
    """
    run = {}
    run['strava_id'] = activity.id
    run['name'] = activity.name
    run['distance'] = activity.distance.num
    run['elapsed_time'] = activity.elapsed_time.total_seconds()
    run['average_speed'] = activity.average_speed.num
    run['average_heartrate'] = activity.average_heartrate
    run['total_elevation_gain'] = activity.total_elevation_gain.num
    run['start_date'] = activity.start_date.timestamp()
    run['title'] = activity.name
    run['description'] = activity.description
    return run


def fetch_runs(user):
    client = Client(access_token=user['strava_token'])
    runs = []
    for activity in client.get_activities(limit=10):
        if activity.type != 'Run':
            continue
        runs.append(activity2run(activity))
    return runs


if __name__ == '__main__':
    push_to_dataservice(fetch_all_runs())
