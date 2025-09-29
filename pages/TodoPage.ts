import { BasePage } from "./BasePage";

export class TodoPage extends BasePage {
    readonly todoInput = 'input.new-todo';
    readonly todoList = 'ul.todo-list';
    readonly todoItems = `${this.todoList} li`;
    readonly clearCompletedButton = 'button.clear-completed';
    readonly itemsLeftCount = 'span.todo-count strong';
    readonly filterAll = 'a[href="#/"]';
    readonly filterActive = 'a[href="#/active"]';
    readonly filterCompleted = 'a[href="#/completed"]';
    readonly toggleAll = 'input.toggle-all';
    }   
