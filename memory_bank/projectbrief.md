создай файл frame_parse.py
операясь на файл main.py, напиши скраппер который берет ссылки на модели в toyota_jdm_models.json переходит по ним и парсит frames(кузова) и записывает в их в файл toyota_jdm_frames.json беря за основу структуру файла toyota_jdm_models.json и записывает frames и соответствующие им ссылки вложением в соответствующюю models. расширь логирование и учитывай таймауты при запросах
вот часть html страницы для выявления нужных селекторов
<table width="100%">
<tbody>
<tr>
<td nowrap="nowrap">
</td><td nowrap="nowrap"><ul class="category2"><li><h4><a href="/corolla_spacio/ae111n/">AE111N</a></h4></li></ul>
<ul class="category2"><li><h4><a href="/corolla_spacio/ae115n/">AE115N</a></h4></li></ul>
</td><td nowrap="nowrap"><ul class="category2"><li><h4><a href="/corolla_spacio/nze121n/">NZE121N</a></h4></li></ul>
<ul class="category2"><li><h4><a href="/corolla_spacio/zze122n/">ZZE122N</a></h4></li></ul>
</td><td nowrap="nowrap"><ul class="category2"><li><h4><a href="/corolla_spacio/zze124n/">ZZE124N</a></h4></li></ul>
</td></tr></tbody></table>