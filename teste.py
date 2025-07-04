#importa todas as bibliotecas que serão utilizadas no código
import face_recognition
from sklearn import svm
from os import listdir, makedirs
from os.path import isdir, join, exists
import joblib
from PIL import Image
from numpy import asarray
import cv2
import os #as = apelido
import mediapipe as mp #Rede Neural Convolucional 
import time

# --- CONFIGURAÇÕES de diretorios que estão armazenados localmente, no disco ridigo do pc---
DIR_FOTOS = r"C:\\Users\\lucas\\OneDrive\\Desktop\\ATP\\Fotos\\"
DIR_FACES = r"C:\\Users\\lucas\\OneDrive\\Desktop\\ATP\\Faces\\"
DIR_TESTE = r"C:\\Users\\lucas\\OneDrive\\Desktop\\ATP\\Teste\\"
DIR_RESULTADO = r"C:\\Users\\lucas\\OneDrive\\Desktop\\ATP\\Resultados\\"

#não é um diretorio, pq é o modelo que está sendo criado quando roda esse codigo.
CAMINHO_MODELO = "modelo_reconhecimento.pkl"

# --- INICIALIZA DETECTORES de pessoas 
mp_face_detection = mp.solutions.face_detection
detector_face = mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5)

mp_face_mesh = mp.solutions.face_mesh
detector_malha = mp_face_mesh.FaceMesh(refine_landmarks=True, max_num_faces=1, min_detection_confidence=0.5)

# --- EXTRAÇÃO DE FACE COM MEDIAPIPE, configura a resolução da face por 180x180---
def extrair_face(arquivo, size=(180, 180)):
    img = Image.open(arquivo).convert('RGB')
    vetor = asarray(img)
    img_bgr = cv2.cvtColor(vetor, cv2.COLOR_RGB2BGR)
    resultado = detector_face.process(img_bgr)

    if not resultado.detections:
        print(f"[AVISO] Nenhuma face detectada em: {arquivo}")
        return None
    #configuração de retangulo facial:  
    bbox = resultado.detections[0].location_data.relative_bounding_box
    h, w, _ = vetor.shape
    x1 = int(bbox.xmin * w)
    y1 = int(bbox.ymin * h)
    x2 = int((bbox.xmin + bbox.width) * w)
    y2 = int((bbox.ymin + bbox.height) * h)
    x1, y1 = max(x1, 0), max(y1, 0)
    x2, y2 = min(x2, w), min(y2, h)

    face = vetor[y1:y2, x1:x2]
    image = Image.fromarray(face).resize(size)
    return image
# cria vetores facias com base nas coordenadas do rosto 👆


#flipa a imagem -- inverte a imagem 
def flip_image(image):
    return image.transpose(Image.FLIP_LEFT_RIGHT)


#carregar fotos das pastas e sub_pastas 
#pasta = src
#subpasta = target
def load_fotos(diretorio_src, diretorio_target):
    if not exists(diretorio_target):
        makedirs(diretorio_target)

    #para cada arquivo na lista de pastas entre e procure o arquivo jpeg, png e jpg e flipa elas e salva 
    for filename in listdir(diretorio_src):
        path = join(diretorio_src, filename)
        path_tg = join(diretorio_target, filename)
        path_tg_flip = join(diretorio_target, "flip-" + filename)

        if not path.lower().endswith(('.png', '.jpg', '.jpeg')):
            continue

        face = extrair_face(path)
        if face is not None:
            face.save(path_tg)
            flip = flip_image(face)
            flip.save(path_tg_flip)

#carrega o diretorio

#pasta = src 
#subpasta = target
def carregar_dir(diretorio_src, diretorio_target):
    #para cada subpasta em lista de pastas(pasta) 
    for subdir in listdir(diretorio_src):
        path = join(diretorio_src, subdir)
        path_tg = join(diretorio_target, subdir)

        if not isdir(path):
            continue

        if not exists(path_tg):
            makedirs(path_tg)

        load_fotos(path, path_tg)

#treina o reconhecedor de reconhecimento facial
def treinar_reconhecedor(diretorio_faces, caminho_modelo=CAMINHO_MODELO):
    encodings = []
    nomes = []

    for pessoa in listdir(diretorio_faces):
        caminho_pessoa = join(diretorio_faces, pessoa)
        if not isdir(caminho_pessoa):
            continue

        for img_nome in listdir(caminho_pessoa):
            img_path = join(caminho_pessoa, img_nome)
            imagem = face_recognition.load_image_file(img_path)
            codificacoes = face_recognition.face_encodings(imagem)

            if not codificacoes:
                print(f"[AVISO] Nenhuma face em {img_path}")
                continue

            encodings.append(codificacoes[0])
            nomes.append(pessoa)

    clf = svm.SVC(gamma='scale', probability=True)
    clf.fit(encodings, nomes)
    joblib.dump(clf, caminho_modelo)
    print(f"[INFO] Modelo salvo em: {caminho_modelo}")

#desenha os resultados com base na probalidade descrita acima
def desenhar_resultados(imagem_bgr, resultados):
    #para cada probalidade top rigth bottom e left = quadrado de reconhecer face nos resultados
    for nome, prob, (top, right, bottom, left) in resultados:
        cor = (0, 255, 0) if prob > 0.80 else (0, 0, 255)
        cv2.rectangle(imagem_bgr, (left, top), (right, bottom), cor, 2)
        texto = f"{nome} ({prob:.2f})"
        cv2.putText(imagem_bgr, texto, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, cor, 2)
    return imagem_bgr


#reconhece o caminho modelo e faz o modelo reconhecimento
def reconhecer_em_diretorio(diretorio_testes, caminho_modelo=CAMINHO_MODELO, salvar_em=None):
    clf = joblib.load(caminho_modelo)
#PARA CADA IMAGEM DE NOME EM LISTAS DE DIRETORIOS
    for nome_img in listdir(diretorio_testes):
        caminho_img = join(diretorio_testes, nome_img)
        if not caminho_img.lower().endswith(('.jpg', '.jpeg', '.png')):
            continue

        imagem = face_recognition.load_image_file(caminho_img)
        localizacoes = face_recognition.face_locations(imagem)
        codificacoes = face_recognition.face_encodings(imagem, localizacoes)

        resultados = []
        for encoding, loc in zip(codificacoes, localizacoes):
            nome = clf.predict([encoding])[0]
            prob = clf.predict_proba([encoding]).max()
            if prob < 0.80:
                nome = "Desconhecido"
            resultados.append((nome, prob, loc))

        imagem_bgr = cv2.cvtColor(imagem, cv2.COLOR_RGB2BGR)
        imagem_com_anotacoes = desenhar_resultados(imagem_bgr, resultados)

        if salvar_em:
            if not os.path.exists(salvar_em):
                os.makedirs(salvar_em)
            caminho_saida = join(salvar_em, f"rot-{nome_img}")
            cv2.imwrite(caminho_saida, imagem_com_anotacoes)
            print(f"[SALVO] {caminho_saida}")
        else:
            cv2.imshow("Resultado", imagem_com_anotacoes)
            cv2.waitKey(0)

    cv2.destroyAllWindows()

# --- VERIFICAÇÃO DE VIVACIDADE (piscadas) --- (isso aq é apenas algo teste não leve em consideração, mas isso aqui detecta piscadas no codigo que vamos apresentar essa função não existe)
def detectar_vivacidade(frame):
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    resultado = detector_malha.process(rgb)

    if not resultado.multi_face_landmarks:
        return False

    olhos_fechados = 0
    for face_landmarks in resultado.multi_face_landmarks:
        pontos = face_landmarks.landmark

        olho_esquerdo = [pontos[159].y, pontos[145].y]
        olho_direito = [pontos[386].y, pontos[374].y]

        if abs(olho_esquerdo[0] - olho_esquerdo[1]) < 0.01:
            olhos_fechados += 1
        if abs(olho_direito[0] - olho_direito[1]) < 0.01:
            olhos_fechados += 1

    return olhos_fechados >= 2

# --- CÂMERA COM RECONHECIMENTO E VIVACIDADE ---
def reconhecer_camera_ao_vivo(caminho_modelo=CAMINHO_MODELO):
    clf = joblib.load(caminho_modelo)
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("[ERRO] Não foi possível acessar a câmera.")
        return

    piscadas_detectadas = 0
    tempo_inicio = time.time()

    print("[INFO] Pressione 'q' para sair.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if detectar_vivacidade(frame):
            piscadas_detectadas += 1
            print(f"[INFO] Piscada detectada: {piscadas_detectadas}")
            time.sleep(0.5)  # Evita contagem duplicada

        if piscadas_detectadas >= 2:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            localizacoes = face_recognition.face_locations(rgb_frame)
            codificacoes = face_recognition.face_encodings(rgb_frame, localizacoes)

            resultados = []
            for encoding, loc in zip(codificacoes, localizacoes):
                prob = clf.predict_proba([encoding]).max()
                if prob < 0.80:
                    nome = "Desconhecido"
                else:
                    nome = clf.predict([encoding])[0]
                resultados.append((nome, prob, loc))

            frame_anotado = desenhar_resultados(frame, resultados)
            cv2.imshow("Reconhecimento Facial ao Vivo", frame_anotado)
        else:
            cv2.putText(frame, "Pisque 2 vezes para verificar vivacidade", (30, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.imshow("Reconhecimento Facial ao Vivo", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# --- EXECUÇÃO ---
if __name__ == '__main__':
    print("[1] Extraindo faces e salvando em 180x180...")
    carregar_dir(DIR_FOTOS, DIR_FACES)

    print("[2] Treinando o modelo SVM...")
    treinar_reconhecedor(DIR_FACES, CAMINHO_MODELO)

    print("[3] Reconhecendo imagens do diretório de testes...")
    reconhecer_em_diretorio(DIR_TESTE, CAMINHO_MODELO, salvar_em=DIR_RESULTADO)

    print("[4] Abrindo câmera ao vivo com verificação de vivacidade...")
    reconhecer_camera_ao_vivo()
