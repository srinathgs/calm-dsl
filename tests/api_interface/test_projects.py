import pytest
from ruamel import yaml
import uuid

from calm.dsl.cli.main import get_api_client
from calm.dsl.cli.projects import (
    poll_creation_status,
    poll_updation_status,
    poll_deletion_status,
)


class TestProjects:
    def test_projects_list(self):

        client = get_api_client()

        params = {"length": 20, "offset": 0}
        res, err = client.blueprint.list(params=params)

        if not err:
            print("\n>> Projects list call successful >>")
            assert res.ok is True
        else:
            pytest.fail("[{}] - {}".format(err["code"], err["error"]))

    def test_projects_crud(self):

        client = get_api_client()
        file_location = "tests/api_interface/entity_spec/sample_project.json"
        project_payload = yaml.safe_load(open(file_location, "r").read())

        payload = {
            "api_version": "3.0",
            "metadata": {"kind": "project"},
            "spec": project_payload,
        }

        project_name = "test_proj" + str(uuid.uuid4())[-10:]
        payload["spec"]["project_detail"]["name"] = project_name

        print("\nCreating project ...")
        res, err = client.project.create(payload)
        if err:
            pytest.fail("[{}] - {}".format(err["code"], err["error"]))

        else:
            assert res.ok is True
            res = res.json()
            assert project_name == res["spec"]["project_detail"]["name"]
            project_uuid = res["metadata"]["uuid"]
            poll_creation_status(client, project_uuid)
            print("\n>> Project created >>")
            print(">> Project Name: {} >>".format(project_name))
            print(">> Project uuid: {} >>".format(project_uuid))

        print("\nReading project ...")
        res, err = client.project.read(project_uuid)
        if err:
            pytest.fail("[{}] - {}".format(err["code"], err["error"]))

        else:
            assert res.ok is True
            res = res.json()
            print(">> Get call to project is successful >>")

        print("\nUpdating project ...")
        file_location = "tests/api_interface/entity_spec/sample_project_update.json"
        project_payload = yaml.safe_load(open(file_location, "r").read())
        spec_version = res["metadata"]["spec_version"]

        payload = {
            "api_version": "3.0",
            "metadata": {
                "kind": "project",
                "uuid": project_uuid,
                "spec_version": spec_version,
            },
            "spec": project_payload,
        }

        project_name = "test_proj" + str(uuid.uuid4())[-10:]
        payload["spec"]["project_detail"]["name"] = project_name

        res, err = client.project.update(project_uuid, payload)
        if err:
            pytest.fail("[{}] - {}".format(err["code"], err["error"]))

        else:
            assert res.ok is True
            res = res.json()
            assert project_name == res["spec"]["project_detail"]["name"]
            poll_updation_status(client, project_uuid, spec_version)
            print(">> Project updated >>")

        print("\nDeleting project ...")
        res, err = client.project.delete(project_uuid)
        if err:
            pytest.fail("[{}] - {}".format(err["code"], err["error"]))

        else:
            assert res.ok is True
            res = res.json()
            poll_deletion_status(client, project_name)
            print("\n>> Project deleted >>")
