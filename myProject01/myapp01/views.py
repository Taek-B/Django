from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect, render
import urllib.parse
import math

from django.db.models import Q

from myapp01.models import Board, Comment

# Create your views here.

UPLOAD_DIR = 'C:/Django_study/upload/'


# write_form
# 함수가 컨트롤러 역할
def write_form(request):
    return render(request, 'board/write.html')


# insert
# csrf를 무시하겠다.
@csrf_exempt
def insert(request):
    fname = ''
    fsize = 0

    if 'file' in request.FILES:
        file = request.FILES['file']
        fname = file.name
        fsize = file.size

        fp = open('%s%s' % (UPLOAD_DIR, fname), 'wb')
        for chunk in file.chunks():
            fp.write(chunk)
        fp.close()

    dto = Board(writer=request.POST['writer'],
                title=request.POST['title'],
                content=request.POST['content'],
                filename=fname,
                filesize=fsize
                )
    dto.save()
    return redirect('/list/')


# 전체보기
# def list_all(request):
#     boardList = Board.objects.all()
#     # dict형태
#     context = {'boardList': boardList}
#     return render(request, 'board/list.html', context)


# 전체보기 -- 검색
def list(request):
    page = request.GET.get('page', 1)
    # word를 공백으로 지정 가능
    word = request.GET.get('word', '')
    field = request.GET.get('field', 'title')

    # boardCount
    if field == 'all':
        # Q
        # '__' : like랑 같다
        boardCount = Board.objects.filter(Q(writer__contains=word) |
                                          Q(title__contains=word) |
                                          Q(content__contains=word)).count()
    elif field == 'writer':
        boardCount = Board.objects.filter(
            Q(writer__contains=word)).count()
    elif field == 'title':
        boardCount = Board.objects.filter(
            Q(title__contains=word)).count()
    elif field == 'content':
        boardCount = Board.objects.filter(
            Q(content__contains=word)).count()
    else:
        boardCount = Board.objects.all().count()

    # 123 [다음]    [이전]  456 [다음]  [이전] 78

    pageSize = 5    # 한 화면 게시글 수
    blockPage = 3   # 보이는 페이지 수
    currentPage = int(page)

    # 시작위치?
    start = (currentPage-1)*pageSize
    startPage = math.floor((currentPage - 1)/blockPage) * \
        blockPage + 1   # floor : 버림
    endPage = startPage + blockPage - 1
    # 게시글의 전체 페이지 수 = math.ceil(게시글 수 / pageSize)
    totPage = math.ceil(boardCount / pageSize)  # ceil : 올림

    if endPage > totPage:
        endPage = totPage

    # 검색내용
    if field == 'all':
        # Q
        # '__' : like랑 같다
        boardList = Board.objects.filter(Q(writer__contains=word) |
                                         Q(title__contains=word) |
                                         Q(content__contains=word)).order_by('-idx')[start: start + pageSize]
    elif field == 'writer':
        boardList = Board.objects.filter(
            Q(writer__contains=word)).order_by('-idx')[start: start + pageSize]
    elif field == 'title':
        boardList = Board.objects.filter(
            Q(title__contains=word)).order_by('-idx')[start: start + pageSize]
    elif field == 'content':
        boardList = Board.objects.filter(
            Q(content__contains=word)).order_by('-idx')[start: start + pageSize]
    else:
        boardList = Board.objects.all().order_by(
            '-idx')[start: start + pageSize]

    # dict형태
    context = {'boardList': boardList,
               'startPage': startPage,
               'blockPage': blockPage,
               'endPage': endPage,
               'totPage': totPage,
               'boardCount': boardCount,
               'currentPage': currentPage,
               'field': field,
               'word': word,
               'range': range(startPage, endPage+1)}
    return render(request, 'board/list.html', context)


# 상세보기 + 댓글까지 가져오기
def detail_idx(request):
    id = request.GET['idx']
    dto = Board.objects.get(idx=id)
    dto.hit_up()
    dto.save()
    # commentList
    commentList_DTO = Comment.objects.filter(board_idx=id).order_by('-idx')

    return render(request, 'board/detail.html', {'dto': dto, 'commentList': commentList_DTO})


# 상세보기+ 댓글까지 가져오기 (detail/5)
def detail(request, board_idx):
    print('board_idx : ', board_idx)
    dto = Board.objects.get(idx=board_idx)
    dto.hit_up()
    dto.save()
    # commentList
    commentList_DTO = Comment.objects.filter(
        board_idx=board_idx).order_by('-idx')

    return render(request, 'board/detail.html', {'dto': dto, 'commentList': commentList_DTO})


# 수정 폼으로 가기
def update_form(request, board_idx):
    dto = Board.objects.get(idx=board_idx)
    return render(request, 'board/update.html', {'dto': dto})


# 수정
@csrf_exempt
def update(request):

    # 파일을 업로드를 했었을 경우
    id = request.POST['idx']
    dto = Board.objects.get(idx=id)
    fname = dto.filename
    fsize = dto.filesize
    hitcount = dto.hit

    # 파일을 업로드를 안했을 경우 파일객체를 받아옴
    if 'file' in request.FILES:
        file = request.FILES['file']
        fname = file.name
        fsize = file.size

        fp = open('%s%s' % (UPLOAD_DIR, fname), 'wb')
        for chunk in file.chunks():
            fp.write(chunk)
        fp.close()

    update_dto = Board(id,
                       writer=request.POST['writer'],
                       title=request.POST['title'],
                       content=request.POST['content'],
                       filename=fname,
                       filesize=fsize,
                       hit=hitcount
                       )
    update_dto.save()

    return redirect('/list')


# 삭제하기
def delete(request, board_idx):
    dto = Board.objects.get(idx=board_idx)
    dto.delete()
    return redirect('/list')


# 다운로드 횟수
def download_count(request):
    id = request.GET['idx']
    # print('id : ', id)
    dto = Board.objects.get(idx=id)
    dto.down_up()
    dto.save()

    count = dto.down
    # print('count :', count)

    # Spring에 있는 responsebody랑 같다
    # 데이터 값을 받기 위해 !!
    return JsonResponse({'idx': id, 'count': count})


# 다운로드
def download(request):
    id = request.GET['idx']
    dto = Board.objects.get(idx=id)
    path = UPLOAD_DIR + dto.filename

    filename = urllib.parse.quote(dto.filename)
    # print('filename : ', filename)
    with open(path, 'rb') as file:
        response = HttpResponse(file.read(),
                                content_type='application/octet-stream')
        response['Content-Disposition'] = "attachment;filename*=UTF-8 '' {0}".format(
            filename)
    return response


# comment
@csrf_exempt
def comment_insert(request):
    id = request.POST['idx']
    dto = Comment(board_idx=id,
                  # 회원에 대한 정보가 없으므로 'aa'로 대체
                  writer='aa',
                  content=request.POST['content'])
    dto.save()
    return redirect("/detail_idx?idx=" + id)
