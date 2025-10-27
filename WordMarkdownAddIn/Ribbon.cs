using System;
using Office = Microsoft.Office.Core;

namespace WordMarkdownAddIn
{
	public class MarkdownRibbon : Office.IRibbonExtensibility
	{
		private Office.IRibbonUI _ribbon;

		public string GetCustomUI(string ribbonID)
		{
			return @"<customUI xmlns=""http://schemas.microsoft.com/office/2009/07/customui"" onLoad=""OnLoad"">
				<ribbon>
					<tabs>
						<tab id=""tabMarkdown"" label=""Markdown"">
							<group id=""grpFile"" label=""Файл"">
								<button id=""btnOpen"" label=""Открыть .md"" size=""large"" onAction=""OnOpenMd"" />
								<button id=""btnSave"" label=""Сохранить .md"" size=""large"" onAction=""OnSaveMd"" />
								<toggleButton id=""btnPane"" label=""Панель"" size=""normal"" onAction=""OnTogglePane"" />
							</group>
							<group id=""grpFormat"" label=""Форматирование"">
								<button id=""bBold"" label=""Жирный"" onAction=""OnBold"" />
								<button id=""bItalic"" label=""Курсив"" onAction=""OnItalic"" />
								<button id=""bStrike"" label=""Зачеркнуть"" onAction=""OnStrike"" />
								<button id=""bCode"" label=""Код"" onAction=""OnInlineCode"" />
							</group>
							<group id=""grpInsert"" label=""Вставка"">
								<button id=""bH1"" label=""H1"" onAction=""OnH1"" />
								<button id=""bList"" label=""Список -"" onAction=""OnBulletList"" />
								<button id=""bNumList"" label=""Список 1."" onAction=""OnNumberList"" />
								<button id=""bCheckbox"" label=""Чекбокс"" onAction=""OnCheckbox"" />
								<button id=""bTable"" label=""Таблица"" onAction=""OnTable"" />
								<button id=""bLink"" label=""Ссылка"" onAction=""OnLink"" />
								<button id=""bImage"" label=""Изображение"" onAction=""OnImage"" />
								<button id=""bHR"" label=""Разделитель"" onAction=""OnHr"" />
								<button id=""bCodeBlock"" label=""Код-блок"" onAction=""OnCodeBlock"" />
								<button id=""bMermaid"" label=""Mermaid"" onAction=""OnMermaid"" />
								<button id=""bMath"" label=""Формула"" onAction=""OnMath"" />
							</group>
						</tab>
					</tabs>
				</ribbon>
			</customUI>";
		}

		public void OnLoad(Office.IRibbonUI ribbonUI)
		{
			_ribbon = ribbonUI;
		}

		public void OnTogglePane(Office.IRibbonControl control, bool pressed)
		{
			Globals.ThisAddIn.TogglePane();
		}

		public void OnOpenMd(Office.IRibbonControl control)
		{
			Globals.ThisAddIn.PaneControl?.OpenMarkdownFile();
		}

		public void OnSaveMd(Office.IRibbonControl control)
		{
			Globals.ThisAddIn.PaneControl?.SaveMarkdownFile();
		}

		public void OnBold(Office.IRibbonControl control)
		{
			Globals.ThisAddIn.PaneControl?.InsertInline("**", "**");
		}

		public void OnItalic(Office.IRibbonControl control)
		{
			Globals.ThisAddIn.PaneControl?.InsertInline("*", "*");
		}

		public void OnStrike(Office.IRibbonControl control)
		{
			Globals.ThisAddIn.PaneControl?.InsertInline("~~", "~~");
		}

		public void OnInlineCode(Office.IRibbonControl control)
		{
			Globals.ThisAddIn.PaneControl?.InsertInline("`", "`");
		}

		public void OnH1(Office.IRibbonControl control)
		{
			Globals.ThisAddIn.PaneControl?.InsertHeading(1);
		}

		public void OnBulletList(Office.IRibbonControl control)
		{
			Globals.ThisAddIn.PaneControl?.InsertBulletList();
		}

		public void OnNumberList(Office.IRibbonControl control)
		{
			Globals.ThisAddIn.PaneControl?.InsertNumberedList();
		}

		public void OnCheckbox(Office.IRibbonControl control)
		{
			Globals.ThisAddIn.PaneControl?.InsertCheckbox(false);
		}

		public void OnTable(Office.IRibbonControl control)
		{
			Globals.ThisAddIn.PaneControl?.InsertTable(3, 3);
		}

		public void OnLink(Office.IRibbonControl control)
		{
			Globals.ThisAddIn.PaneControl?.InsertLink("текст", "https://example.com");
		}

		public void OnImage(Office.IRibbonControl control)
		{
			Globals.ThisAddIn.PaneControl?.InsertImage("alt", "assets/image.png");
		}

		public void OnHr(Office.IRibbonControl control)
		{
			Globals.ThisAddIn.PaneControl?.InsertSnippet("\n\n---\n\n");
		}

		public void OnCodeBlock(Office.IRibbonControl control)
		{
			Globals.ThisAddIn.PaneControl?.InsertCodeBlock("csharp");
		}

		public void OnMermaid(Office.IRibbonControl control)
		{
			Globals.ThisAddIn.PaneControl?.InsertMermaidSample();
		}

		public void OnMath(Office.IRibbonControl control)
		{
			Globals.ThisAddIn.PaneControl?.InsertMathSample();
		}
	}
}