from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect, render

from myapp01.models import Board

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
def list(request):
    boardList = Board.objects.all()

    # dict형태
    context = {'boardList': boardList}
    return render(request, 'board/list.html', context)


# 상세보기
def detail_idx(request):
    id = request.GET['idx']
    dto = Board.objects.get(idx=id)
    dto.hit_up()
    dto.save()
    return render(request, 'board/detail.html', {'dto': dto})


# 상세보기 (detail/5)
def detail(request, board_idx):
    print('board_idx : ', board_idx)
    dto = Board.objects.get(idx=board_idx)
    dto.hit_up()
    dto.save()
    return render(request, 'board/detail.html', {'dto': dto})


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


def delete(request, board_idx):
    dto = Board.objects.get(idx=board_idx)
    dto.delete()
    return redirect('/list')
