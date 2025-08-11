import pytest
import json
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, date
from googleapiclient.errors import HttpError

from src.tools.tasks_tools import (
    list_task_lists,
    list_tasks,
    search_tasks,
    search_tasks_by_period,
    create_task,
    update_task,
    mark_task_completed
)

class TestListTaskLists:
    @pytest.mark.asyncio
    @patch('src.tools.tasks_tools.asyncio.to_thread')
    async def test_list_task_lists_success(self, mock_to_thread):
        # Mock credentials
        mock_creds = Mock()
        
        # Mock service
        mock_service = Mock()
        mock_service.tasklists().list().execute.return_value = {
            "items": [
                {"id": "list1", "title": "Personal Tasks", "updated": "2024-01-01T00:00:00Z"},
                {"id": "list2", "title": "Work Tasks", "updated": "2024-01-02T00:00:00Z"}
            ]
        }
        
        # Mock task lists response
        mock_response = {
            "items": [
                {"id": "list1", "title": "Personal Tasks", "updated": "2024-01-01T00:00:00Z"},
                {"id": "list2", "title": "Work Tasks", "updated": "2024-01-02T00:00:00Z"}
            ]
        }
        
        # Set up asyncio.to_thread side effects for the three calls:
        # 1. get_credentials() 2. build() 3. _list_task_lists()
        mock_to_thread.side_effect = [mock_creds, mock_service, mock_response]
        
        # Call function
        result = await list_task_lists()
        result_data = json.loads(result)
        
        # Assertions
        assert len(result_data) == 2
        assert result_data[0]["id"] == "list1"
        assert result_data[0]["title"] == "Personal Tasks"
        assert result_data[1]["id"] == "list2"
        assert result_data[1]["title"] == "Work Tasks"
        
        # Verify asyncio.to_thread was called 3 times
        assert mock_to_thread.call_count == 3

    @pytest.mark.asyncio
    @patch('src.tools.tasks_tools.get_credentials')
    @patch('src.tools.tasks_tools.build')
    @patch('src.tools.tasks_tools.asyncio.to_thread')
    async def test_list_task_lists_http_error(self, mock_to_thread, mock_build, mock_get_credentials):
        # Mock credentials
        mock_creds = Mock()
        mock_get_credentials.return_value = mock_creds
        
        # Mock service
        mock_service = Mock()
        mock_build.return_value = mock_service
        
        # Mock HTTP error
        mock_error = HttpError(Mock(status=500), b"Internal Server Error")
        mock_to_thread.side_effect = [mock_creds, mock_service, mock_error]
        
        # Call function
        result = await list_task_lists()
        result_data = json.loads(result)
        
        # Assertions
        assert "error" in result_data
        assert "An error occurred" in result_data["error"]

class TestListTasks:
    @pytest.mark.asyncio
    @patch('src.tools.tasks_tools.validate_task_list_id')
    @patch('src.tools.tasks_tools.get_default_task_max_results')
    @patch('src.tools.tasks_tools.asyncio.to_thread')
    async def test_list_tasks_success(self, mock_to_thread, mock_get_max_results, mock_validate):
        # Mock configuration
        mock_validate.return_value = "@default"
        mock_get_max_results.return_value = 50
        
        # Mock credentials
        mock_creds = Mock()
        
        # Mock service
        mock_service = Mock()
        mock_service.tasks().list().execute.return_value = {
            "items": [
                {"id": "task1", "title": "Task 1", "status": "needsAction"},
                {"id": "task2", "title": "Task 2", "status": "completed"}
            ]
        }
        
        # Mock tasks response
        mock_response = {
            "items": [
                {"id": "task1", "title": "Task 1", "status": "needsAction"},
                {"id": "task2", "title": "Task 2", "status": "completed"}
            ]
        }
        
        # Set up asyncio.to_thread side effects for the three calls:
        # 1. get_credentials() 2. build() 3. _list_tasks()
        mock_to_thread.side_effect = [mock_creds, mock_service, mock_response]
        
        # Call function
        result = await list_tasks()
        result_data = json.loads(result)
        
        # Assertions
        assert len(result_data) == 2
        assert result_data[0]["id"] == "task1"
        assert result_data[0]["taskListId"] == "@default"
        assert result_data[1]["id"] == "task2"
        assert result_data[1]["taskListId"] == "@default"
        
        # Verify asyncio.to_thread was called 3 times
        assert mock_to_thread.call_count == 3

class TestSearchTasks:
    @pytest.mark.asyncio
    @patch('src.tools.tasks_tools.get_credentials')
    @patch('src.tools.tasks_tools.build')
    @patch('src.tools.tasks_tools.asyncio.to_thread')
    @patch('src.tools.tasks_tools.validate_task_list_id')
    @patch('src.tools.tasks_tools.get_default_task_max_results')
    async def test_search_tasks_success(self, mock_get_max_results, mock_validate, mock_to_thread, mock_build, mock_get_credentials):
        # Mock configuration
        mock_validate.return_value = "@default"
        mock_get_max_results.return_value = 50
        
        # Mock credentials
        mock_creds = Mock()
        mock_get_credentials.return_value = mock_creds
        
        # Mock service
        mock_service = Mock()
        mock_build.return_value = mock_service
        
        # Mock tasks response
        mock_response = {
            "items": [
                {"id": "task1", "title": "Important meeting", "notes": "Discuss project timeline"},
                {"id": "task2", "title": "Buy groceries", "notes": "Milk, bread, eggs"},
                {"id": "task3", "title": "Review code", "notes": "Check pull request"}
            ]
        }
        
        mock_to_thread.side_effect = [mock_creds, mock_service, mock_response]
        
        # Call function
        result = await search_tasks("meeting")
        result_data = json.loads(result)
        
        # Assertions
        assert len(result_data) == 1
        assert result_data[0]["id"] == "task1"
        assert "meeting" in result_data[0]["title"].lower()

class TestSearchTasksByPeriod:
    @pytest.mark.asyncio
    @patch('src.tools.tasks_tools.get_credentials')
    @patch('src.tools.tasks_tools.build')
    @patch('src.tools.tasks_tools.asyncio.to_thread')
    @patch('src.tools.tasks_tools.validate_task_list_id')
    @patch('src.tools.tasks_tools.get_default_task_max_results')
    async def test_search_tasks_by_period_success(self, mock_get_max_results, mock_validate, mock_to_thread, mock_build, mock_get_credentials):
        # Mock configuration
        mock_validate.return_value = "@default"
        mock_get_max_results.return_value = 50
        
        # Mock credentials
        mock_creds = Mock()
        mock_get_credentials.return_value = mock_creds
        
        # Mock service
        mock_service = Mock()
        mock_build.return_value = mock_service
        
        # Mock tasks response
        mock_response = {
            "items": [
                {"id": "task1", "title": "Task 1", "due": "2024-01-15T00:00:00Z"},
                {"id": "task2", "title": "Task 2", "due": "2024-01-20T00:00:00Z"},
                {"id": "task3", "title": "Task 3", "due": "2024-01-25T00:00:00Z"}
            ]
        }
        
        mock_to_thread.side_effect = [mock_creds, mock_service, mock_response]
        
        # Call function
        result = await search_tasks_by_period("2024-01-15", "2024-01-20")
        result_data = json.loads(result)
        
        # Assertions
        assert len(result_data) == 2
        assert result_data[0]["id"] == "task1"
        assert result_data[1]["id"] == "task2"

class TestCreateTask:
    @pytest.mark.asyncio
    @patch('src.tools.tasks_tools.validate_task_list_id')
    @patch('src.tools.tasks_tools.asyncio.to_thread')
    async def test_create_task_success(self, mock_to_thread, mock_validate):
        # Mock configuration
        mock_validate.return_value = "@default"
        
        # Mock credentials
        mock_creds = Mock()
        
        # Mock service
        mock_service = Mock()
        mock_service.tasks().insert().execute.return_value = {
            "id": "new_task_123",
            "title": "New Task",
            "notes": "Task description",
            "status": "needsAction"
        }
        
        # Mock created task response
        mock_response = {
            "id": "new_task_123",
            "title": "New Task",
            "notes": "Task description",
            "status": "needsAction"
        }
        
        # Set up asyncio.to_thread side effects for the three calls:
        # 1. get_credentials() 2. build() 3. _create_task()
        mock_to_thread.side_effect = [mock_creds, mock_service, mock_response]
        
        # Call function
        result = await create_task("New Task", description="Task description")
        result_data = json.loads(result)
        
        # Assertions
        assert result_data["id"] == "new_task_123"
        assert result_data["title"] == "New Task"
        assert result_data["notes"] == "Task description"
        assert result_data["taskListId"] == "@default"
        
        # Verify asyncio.to_thread was called 3 times
        assert mock_to_thread.call_count == 3

    @pytest.mark.asyncio
    @patch('src.tools.tasks_tools.get_credentials')
    @patch('src.tools.tasks_tools.build')
    @patch('src.tools.tasks_tools.asyncio.to_thread')
    @patch('src.tools.tasks_tools.validate_task_list_id')
    async def test_create_task_with_due_date(self, mock_validate, mock_to_thread, mock_build, mock_get_credentials):
        # Mock configuration
        mock_validate.return_value = "@default"
        
        # Mock credentials
        mock_creds = Mock()
        mock_get_credentials.return_value = mock_creds
        
        # Mock service
        mock_service = Mock()
        mock_build.return_value = mock_service
        
        # Mock created task response
        mock_response = {
            "id": "new_task_123",
            "title": "Due Task",
            "due": "2024-01-31T00:00:00Z"
        }
        
        mock_to_thread.side_effect = [mock_creds, mock_service, mock_response]
        
        # Call function
        result = await create_task("Due Task", due_date="2024-01-31")
        result_data = json.loads(result)
        
        # Assertions
        assert result_data["id"] == "new_task_123"
        assert result_data["title"] == "Due Task"
        assert "2024-01-31" in result_data["due"]

class TestUpdateTask:
    @pytest.mark.asyncio
    @patch('src.tools.tasks_tools.validate_task_list_id')
    @patch('src.tools.tasks_tools.asyncio.to_thread')
    async def test_update_task_success(self, mock_to_thread, mock_validate):
        # Mock configuration
        mock_validate.return_value = "@default"
        
        # Mock credentials
        mock_creds = Mock()
        
        # Mock service
        mock_service = Mock()
        mock_service.tasks().patch().execute.return_value = {
            "id": "task_123",
            "title": "Updated Task",
            "notes": "Updated description",
            "status": "completed"
        }
        
        # Mock updated task response
        mock_response = {
            "id": "task_123",
            "title": "Updated Task",
            "notes": "Updated description",
            "status": "completed"
        }
        
        # Set up asyncio.to_thread side effects for the three calls:
        # 1. get_credentials() 2. build() 3. _update_task()
        mock_to_thread.side_effect = [mock_creds, mock_service, mock_response]
        
        # Call function
        result = await update_task("task_123", title="Updated Task", description="Updated description", status="completed")
        result_data = json.loads(result)
        
        # Assertions
        assert result_data["id"] == "task_123"
        assert result_data["title"] == "Updated Task"
        assert result_data["notes"] == "Updated description"
        assert result_data["status"] == "completed"
        
        # Verify asyncio.to_thread was called 3 times
        assert mock_to_thread.call_count == 3

class TestMarkTaskCompleted:
    @pytest.mark.asyncio
    @patch('src.tools.tasks_tools.validate_task_list_id')
    @patch('src.tools.tasks_tools.datetime')
    @patch('src.tools.tasks_tools.asyncio.to_thread')
    async def test_mark_task_completed_success(self, mock_to_thread, mock_datetime, mock_validate):
        # Mock configuration
        mock_validate.return_value = "@default"
        
        # Mock datetime
        mock_now = datetime(2024, 1, 15, 12, 0, 0)
        mock_datetime.utcnow.return_value = mock_now
        
        # Mock credentials
        mock_creds = Mock()
        
        # Mock service
        mock_service = Mock()
        mock_service.tasks().patch().execute.return_value = {
            "id": "task_123",
            "title": "Completed Task",
            "status": "completed",
            "completed": "2024-01-15T12:00:00Z"
        }
        
        # Mock updated task response
        mock_response = {
            "id": "task_123",
            "title": "Completed Task",
            "status": "completed",
            "completed": "2024-01-15T12:00:00Z"
        }
        
        # Set up asyncio.to_thread side effects for the three calls:
        # 1. get_credentials() 2. build() 3. _update_task()
        mock_to_thread.side_effect = [mock_creds, mock_service, mock_response]
        
        # Call function
        result = await mark_task_completed("task_123", completed=True)
        result_data = json.loads(result)
        
        # Assertions
        assert result_data["id"] == "task_123"
        assert result_data["status"] == "completed"
        assert result_data["completed"] == "2024-01-15T12:00:00Z"
        
        # Verify asyncio.to_thread was called 3 times
        assert mock_to_thread.call_count == 3

    @pytest.mark.asyncio
    @patch('src.tools.tasks_tools.validate_task_list_id')
    @patch('src.tools.tasks_tools.asyncio.to_thread')
    async def test_mark_task_incomplete_success(self, mock_to_thread, mock_validate):
        # Mock configuration
        mock_validate.return_value = "@default"
        
        # Mock credentials
        mock_creds = Mock()
        
        # Mock service
        mock_service = Mock()
        mock_service.tasks().patch().execute.return_value = {
            "id": "task_123",
            "title": "Incomplete Task",
            "status": "needsAction"
        }
        
        # Mock updated task response
        mock_response = {
            "id": "task_123",
            "title": "Incomplete Task",
            "status": "needsAction"
        }
        
        # Set up asyncio.to_thread side effects for the three calls:
        # 1. get_credentials() 2. build() 3. _update_task()
        mock_to_thread.side_effect = [mock_creds, mock_service, mock_response]
        
        # Call function
        result = await mark_task_completed("task_123", completed=False)
        result_data = json.loads(result)
        
        # Assertions
        assert result_data["id"] == "task_123"
        assert result_data["status"] == "needsAction"
        
        # Verify asyncio.to_thread was called 3 times
        assert mock_to_thread.call_count == 3
